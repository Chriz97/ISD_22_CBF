# ISD_22_Cross_Border_Finance

What does the Cross Border Finance Website offer you?

- An overview of the Dow Jones Industrial Average
- Briefly explains how the DOW is calculated daily
- Stock Market Fundamentals which is even helpful for sophisticated traders
- A unique Value Model which helps user to recognize overvalued and undervalued stocks (Please note that for CRM, DOW, GS and V the calculation for the Value Model is   not possible since the date of the IPO of these companies was much later than of all other companies)

Our Application which is based on Flask and uses Github for the VCS-Implementation:

	Progamming Languages are: HTML, CSS, Python and the usage of Pyscript to implement the Matplotlib Graphs.
	
	The Design is mainly based on the Bootstrap Repository and we also use 3 CSS Files.

	Data is either derived from the API (Alphavantage API) for Stock Prices or Excel Files (Financial Information and the Value Model).
	The Excel files are either filled with Information from the Alphavantage API (Risk Free Rates, Quarterly Earning per Share, Consumer Price Index)
	or from Google Finance (Historical Share Prices) or from Microsoft Finance (Financial Fundamentals)

	Web Hosting: Rented Webspace (Virtual Environment), can be accessed via the following link: http://195.201.141.191:5000/ 

The Website:

Registration:

 - SQLITE Database in the Instance Folder: To handle User information (First Name, Last Name, Username, Email, Password)
 - User receives an email when he registers on the Website (Google SMTP Server)

Login:

- Users have to login with their Username and Password which leads them to: the 2 Factor Authentication Website
- 2FA: Users have to create a Google Authenticator Account with the Username and the Secret Token in order to successfully login

Home Page:

- Stock Market Ticker
- Description of the Dow Jones Industrial Average and how it is calculated
- Overview of the 30 Dow Companies, Ticker Symbol, Industry and Index Weighting

30 Dow Jones Companies: (30 Different HTML Templates can be accessed from the Home Page):

- Behind "Paywall": Users have to register and login in order to see the Value Model
	and the Financial Fundamentals (Flask Login: @LoginRequired)
- Financial Fundamentals (Stock Price, 52 Week High, 52 Week Low, Beta and many more)
- Graph that displays the Value Model (Created with Matplotlib and implemented with Pyscript)
- 2 Second Graph Inflation Adjusted EPS

Value Model:
