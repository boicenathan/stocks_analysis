# Stocks Analysis
## Initial setup
I recommend that you download [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/) and use that to manage
this project. They have a great tutorial [here](https://www.jetbrains.com/help/pycharm/quick-start-guide.html#create) that
walks you through the process of setting up a project and installing Python. This code should work fine for Python >= 3.9

The project is located on GitHub [here](https://github.ibm.com/nboice/stocks_analysis). You can either 
download the project or [clone it by connecting your GitHub to PyCharm](https://www.jetbrains.com/help/pycharm/github.html#register-account). 

Next, add a YAML file to the config folder with `key` and `host` values provided by the Yahoo Finance API.  The path should look like `config/parameters.yaml`.

Go to the Nasdaq [website](https://www.nasdaq.com/market-activity/stocks/screener) and download a csv of all the tickers.  Place that file in the data folder so it shows as `data/symbols.csv`.

Now that you have all the files you need, create a fresh virtual environment for this project. Then, open PyCharm's terminal
interface and run the command `pip install -r config/requirements.txt`.

Once complete, the program will export the results into the data folder with the current date.

### Configurations
This script will run as many tickers as it can until it recieves a `429` status code or has 50 or less requests remaining.  
I use the basic free API plan which limits to 500 requests per month and 5 requests per second.  There is a function in 
the program that calculates the time between requests and will pause if it goes too fast.  You can also update `line 15` 
to the price range of the stocks you would like to analyze.

The `historical.py` script will take the outputs from the regular pulls and check if the last closing price has met the
target price and if so, when.