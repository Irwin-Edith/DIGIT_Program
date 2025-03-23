
from digit_interface.digit import Digit 
from digit_interface.digit_handler import DigitHandler 

# Change D12345 to your DIGIT serial number, 
# and specify a friendly name 

digit = Digit("D00045", "HAND")
digit.connect()  

# Print device info 
print(digit.info())  

# Display stream obtained from DIGIT  
digit.show_view()  

# Disconnect DIGIT stream 
digit.disconnect()

# handler = DigitHandler()
# digits = handler.list_digits()
# print(digits)
