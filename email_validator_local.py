# email_validator_local.py
import dns.resolver
import smtplib
import pandas as pd
from email_validator import validate_email, EmailNotValidError
from disposable_email_domains import blocklist
from tqdm import tqdm
import time
import sys
from smtp_server import start_smtp_server

def print_status(email, status, details):
    print(f"\r\033[K{email}: {status} - {details}", flush=True)

def is_disposable(domain):
    return domain.lower() in blocklist

def verify_email(email):
    try:
        print_status(email, "Checking", "Syntax validation...")
        # Step 1: Syntax validation
        valid = validate_email(email)
        normalized_email = valid.email
        domain = email.split('@')[1]
        
        # Step 2: DNS and MX record verification
        print_status(email, "Checking", "DNS records...")
        try:
            mx_records = dns.resolver.resolve(domain, 'MX', lifetime=10)
            mx_record_exists = bool(mx_records)
        except Exception as e:
            print_status(email, "Failed", f"No valid MX records: {str(e)}")
            return {
                'email': email,
                'is_valid': False,
                'error': 'No valid MX records'
            }
        
        # Step 3: SMTP verification using local server
        print_status(email, "Checking", "SMTP connection...")
        try:
            smtp = smtplib.SMTP('127.0.0.1', 1025, timeout=10)
            smtp.set_debuglevel(1)  # Enable debugging
            smtp.ehlo('test.com')
            
            # Try to verify recipient
            smtp.mail('test@test.com')
            code, message = smtp.rcpt(email)
            smtp_valid = (code >= 200 and code <= 299)
            
            smtp.quit()
        except Exception as e:
            smtp_valid = False
            print_status(email, "Warning", f"SMTP check failed: {str(e)}")
        
        # Step 4: Spam trap and disposable email detection
        print_status(email, "Checking", "Disposable email check...")
        is_disposable_email = is_disposable(domain)
        
        result = {
            'email': email,
            'is_valid': mx_record_exists and smtp_valid and not is_disposable_email,
            'normalized_email': normalized_email,
            'mx_check': 'Pass' if mx_record_exists else 'Fail',
            'smtp_check': 'Pass' if smtp_valid else 'Fail',
            'is_disposable': is_disposable_email
        }
        
        status = "Valid" if result['is_valid'] else "Invalid"
        print_status(email, status, f"MX: {result['mx_check']}, SMTP: {result['smtp_check']}, Disposable: {result['is_disposable']}")
        return result
        
    except EmailNotValidError as e:
        print_status(email, "Invalid", str(e))
        return {
            'email': email,
            'is_valid': False,
            'error': str(e)
        }

def validate_emails(file_path):
    # Start local SMTP server
    print("Starting local SMTP server...")
    smtp_thread = start_smtp_server()
    
    print(f"\nReading file: {file_path}")
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            emails = df['email'].tolist()
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
            emails = df['email'].tolist()
        elif file_path.endswith('.txt'):
            with open(file_path, 'r') as file:
                emails = [line.strip() for line in file]
        else:
            raise ValueError('Unsupported file format')
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

    print(f"\nFound {len(emails)} emails to validate")
    print("\nStarting validation process...")
    time.sleep(1)

    results = []
    for email in tqdm(emails, desc="Progress", unit="email"):
        results.append(verify_email(email))
        
    print("\nSaving results...")
    results_df = pd.DataFrame(results)
    output_file = 'validation_results.csv'
    results_df.to_csv(output_file, index=False)
    
    valid_count = sum(1 for r in results if r['is_valid'])
    print(f"\nValidation Complete!")
    print(f"Total emails: {len(emails)}")
    print(f"Valid emails: {valid_count}")
    print(f"Invalid emails: {len(emails) - valid_count}")
    print(f"Results saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python email_validator_local.py <path_to_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    validate_emails(file_path)
