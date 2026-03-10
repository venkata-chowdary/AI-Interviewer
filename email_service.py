FROM_NAME = "AI Interviewer"


async def send_verification_email(to_email: str, otp: str) -> None:
    """
    Development-only email sender.

    Does NOT send real emails; it just logs the OTP to stdout
    so you can read it from the backend logs.
    """
    print("=== Verification Email (dev only, no real email sent) ===")
    print(f"To: {to_email}")
    print("Subject: Your email verification code")
    print()
    print("Hi,")
    print()
    print(f"Your email verification code is: {otp}")
    print("This code is valid for 10 minutes.")
    print()
    print("Thanks,")
    print(FROM_NAME)
