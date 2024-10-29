import pyshorteners

# Take the long URL as input from the user
long_url = input("Enter the URL to shorten: ")

# Initialize the Shortener
shortener = pyshorteners.Shortener()

# Shorten the URL using TinyURL service
short_url = shortener.tinyurl.short(long_url)

# Print the shortened URL
print("The Shortened URL is:", short_url)
