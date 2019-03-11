#!/usr/bin/env python

import zeep
import os
import argparse
import yaml
import coloredlogs
import logging
import uuid
import json
import datetime
import pushover
import shelve

#Setup logging
coloredlogs.install(level="INFO")
log = logging.getLogger("main")

class MediSnip(object):
    MEDICOVER_API = "https://api.medicover.pl/MOB/MOB.WebServices/Service.svc/basic?singleWsdl"
    def __init__(self, configuration_file="medisnip.yaml"):
        #Setup logger
        self.log = logging.getLogger("medisnip")
        self.log.info("MediSnip logger initialized")
        #Open configuration file
        try:
            config_data = open(
                os.path.expanduser(
                    configuration_file
                ),
                'r'
            ).read()
        except IOError:
            raise Exception('Cannot open configuration file ({file})!'.format(file=configuration_file))
        #Try to parse yaml configuration
        try:
            self.config = yaml.load(config_data)
        except Exception as yaml_error:
            raise Exception('Configuration problem: {error}'.format(error=yaml_error))
        transport = zeep.Transport()
        transport.session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        self.medicover = zeep.Client(self.MEDICOVER_API, transport=transport)
        self.mol = self.medicover.service
        self.log.info("MediSnip client initialized")
        #Try to login to MOL Service
        ticket = json.loads(self.mol.MobileLogin_StrongTypeInput(
            self.config['medicover']['card_id'], 
            self.config['medicover']['password'], 
            'NewMOB', 
            uuid.uuid4, 
            'Android',
            '7.1'
        ))
        if ticket['TicketId'] is None:
            raise Exception("Login or password is incorrect")
        else:
            self.ticket = ticket['TicketId']
            self.person = ticket['Id']
        self.log.info("Succesfully logged in! (TicketID: {ticket}, PersonID: {person})".format(
            ticket=self.ticket,
            person=self.person
        ))
    
    def list_codes(self):
        # Region -> Specialty -> Clinic -> Doctor
        self.log.info('Listing available ids!')
        #Region
        for region in self.mol.LoadRegions(
            ticketId=self.ticket,
            input={}
        ):
            #Specialty (cached)
            specialties = self.mol.LoadSpecialties_Cached(
                    ticketId=self.ticket,
                    input={
                        'RegionId': region['RegionId']
                    }
                )
            if specialties:
                for specialty in specialties:
                    #Clinics (cached)
                    clinics = self.mol.LoadClinics_Cached(
                        ticketId=self.ticket,
                        input={
                            'SpecialtyId': specialty['SpecialtyId'],
                            'RegionId': region['RegionId']
                        }
                    )
                    if clinics:
                        for clinic in clinics:
                            #Load doctors (cached):
                            doctors = self.mol.LoadDoctors_Cached(
                                ticketId=self.ticket,
                                input={
                                    'SpecialtyId': specialty['SpecialtyId'],
                                    'RegionId': region['RegionId'],
                                    'ClinicId': clinic['ClinicId']
                                }
                            )
                            if doctors:
                                for doctor in doctors:
                                    self.log.info(u"DoctorLocatorID: {id} for: Location: {RegionPublicName} {ClinicPublicName} Specialty: {SpecialtyName} Doctor: {DoctorName}".format(
                                        id="{}-{}-{}-{}".format(
                                            region['RegionId'],
                                            specialty['SpecialtyId'],
                                            clinic['ClinicId'],
                                            doctor['DoctorId']
                                        ),
                                        RegionPublicName=region['RegionPublicName'],
                                        ClinicPublicName=clinic['ClinicPublicName'],
                                        SpecialtyName=specialty['SpecialtyName'],
                                        DoctorName=doctor['DoctorName']
                                    ))
    def check_slots(self):
        try:
            (region_id, specialty_id, clinic_id, doctor_id) = self.config['medisnip']['doctor_locator_id'].strip().split('*')
        except ValueError:
            raise Exception('DoctorLocatorID seems to be in invalid format')
        self.log.info("Searching for appointments.")
        appointments = self.mol.GetFreeSlots(
            ticketId=self.ticket,
            input={
                'RegionId': region_id,
                'SpecialtyId': specialty_id,
                'ClinicId': clinic_id,
                'DoctorId': doctor_id,
                'StartDate': datetime.datetime.now(),
                'EndDate': datetime.datetime.now()+datetime.timedelta(
                    days=self.config['medisnip']['lookup_time_days']
                )
            }
        )
        if appointments:
            for appointment in appointments:
                ap_dict = zeep.helpers.serialize_object(
                            appointment, 
                            target_cls=dict
                        )
                self.log.info("Appointment found ({data})".format(
                    data=str(ap_dict)
                ))
                self._notify(ap_dict, self.config['pushover']['message_template'].format(
                        **ap_dict
                    )
                )
        else:
            self.log.info("No appointments found.")

    def _notify(self, data, message):
        state = shelve.open(self.config['misc']['notifydb'])
        notifications = state.get(str(data['DoctorId']), [])
        if not data['AppointmentDate'] in notifications:
            notifications.append(data['AppointmentDate'])
            self.log.info(u'Sending notification: {}'.format(message))
            pushover.init(self.config['pushover']['api_token'])
            pushover.Client(self.config['pushover']['user_key']).send_message(message, title=self.config['pushover']['title'])
        else:
            self.log.info('Notification was already sent.')
        state[str(data['DoctorId'])] = notifications
        state.close()
                    
if __name__=="__main__":
    log.info("MediSnip - Medicover Appointment Sniper <wajdzik.m@gmail.com>")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        help="Configuration file path", default="~/.medisnip.yml"
    )
    parser.add_argument(
        "-l", "--list", 
        help="List all DoctorLocatorID's (needed for configuration)", action='store_true')
    args = parser.parse_args()
    medisnip = MediSnip(configuration_file=args.config)
    if args.list:
        medisnip.list_codes()
    else:
        medisnip.check_slots()
