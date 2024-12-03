How to Use
==============

1- Save both scripts in the same directory

    git clone https://github.com/Ahmed-Sabri/Emailidator.git

2- Install required packages:
    
    pip install dnspython email-validator disposable-email-domains pandas tqdm aiosmtpd openpyxl

3- Run the validator:

    python email_validator_local.py your_email_list.csv  
    
	    ### NOTE ###
	    Whethe you use txt, or xls, or xlsx, or csv .. all what is required is the first column with the list of emails and the header should be "email"
	
    
Key Features
============

Local SMTP Server:

    Runs on localhost (127.0.0.1) port 1025
    Handles SMTP connections without requiring system-level configuration
    Provides detailed debugging information

Enhanced Validation:

    Uses local SMTP server for connection testing
    Maintains all previous validation features
    Provides detailed error messages and status updates

The local SMTP server allows you to perform SMTP checks without relying on external servers or dealing with ISP restrictions. However, note that this is a simplified implementation and may not catch all invalid email scenarios that a production SMTP server would detect.

