MediSnip - Medicover Appointment Sniper
=======================================
Simple tool to notify about available slot in Medicover medical care service using pushover notifications.
It uses SOAP service which was discovered in sources of Android mobile application.

How to use MediSnip?
--------------------
First of all create virtualenv and install python requirements from requirements.txt

1) For each specialist create configuration file (yaml format) and save it for example as my_favourite_surgeon.yml:
```
medicover:
  card_id: 1234567 # Medicover MRN (your card number)
  password: change.me # Medicover account password
medisnip:
  doctor_locator_id: 123-1234-12345-123456 # Unique identificator of specialist. Can be obtained by running ./medisnip.py -l - beware - listing is slow
  lookup_time_days: 25 # How many days from now should script look at.
pushover:
  user_key: PUSHOVER_USER_KEY # Your pushover.net user key
  api_token: API_TOKEN # pushover.net App API Token
  message_template: "New visit! {AppointmentDate} at {ClinicPublicName} - {DoctorName} ({SpecialtyName})" # Message template, available fields: SpecialtyId ClinicId VendorTypeId ClinicName EndTime HiddenSlot ErrorText ErrorCode DateStartTime VendorTypeCd OARule ClinicPublicName SpecialtyName SysVisitTypeId DoctorLanguages LinkedReferralId DoctorName ConsultationRoomId Position DebugData DoctorScheduleId AppointmentDate ScheduleDate DoctorId ServiceId StartTime Duration
  title: "New visit available!" # Pushover message topic
misc:
  notifydb: ./surgeon_data.db # State file used to remember which notifications has been sent already
```

2) Add script to crontab:
```
*/3 * * * * /path/to/medisnip/venv/bin/python /path/to/medisnip.py -c /path/to/my_favourite_surgeon.yml 
```
(Additionaly you can tune logger settings in script)

3) Wait for new appointment notifications in your pushover app on mobile :)!

License
-------
The MIT License (MIT)

Copyright (c) 2018 Marek Wajdzik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Contact
-------
Marek Wajdzik <wajdzik.m@gmail.com>
