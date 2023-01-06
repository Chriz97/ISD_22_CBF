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

The core idea of the Value Model is, that homogeneous goods should be traded for the same price on the
market. As we don’t have several suppliers with different prices but rather a market, we can´t just simply
take the average and either go long/short with underpriced/overpriced goods. Therefore, we make the
historical prices “more comparable” to today’s prices by using the Shiller price-to-earnings ratio CAPE and
look for a 10-year average of how the market valued the underlying security.
The core assumption of a relational stock value model that uses the Shiller price-to-earnings ratio (CAPE)
for measurement is that the market's long-term average price-to-earnings ratio is a good indicator of the
market's overall valuation. 

The Shiller CAPE is a measure of the market's price-to-earnings ratio that is
based on average earnings over the past 10 years, adjusted for inflation. It is named after economist
Robert Shiller, who developed the measure to account for fluctuations in earnings that can affect the
traditional price-to-earnings ratio.

According to the relational stock value model, if the Shiller CAPE is significantly above its long-term
average, it may indicate that the market is overvalued and that future returns may be lower than average.
Conversely, if the Shiller CAPE is significantly below its long-term average, it may indicate that the market
is undervalued and that future returns may be higher than average.
The relational stock value model assumes that the Shiller CAPE is a reliable indicator of the market's
overall valuation because it considers long-term earnings trends and adjusts for inflation, which can help
to smooth out short-term fluctuations in earnings and provide a more accurate measure of the market's
valuation. However, it is important to note that the Shiller CAPE is just one factor to consider when
evaluating the market and that other factors, such as economic conditions and company-specific
fundamentals, can also influence stock prices.

So basically, this approach is another source of information which ideally supports you in making easier
decisions. 
