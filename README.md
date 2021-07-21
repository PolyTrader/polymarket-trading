# trade-cli
Simple cli tool for trading on PolyMarket

### Installation on Windows
 - Install [Python](https://www.microsoft.com/en-us/p/python-39/9p7qfqmjrfp7?activetab=pivot:overviewtab) from Microsoft
   * or download the [Python installer](https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe) directly 
 - Install [Visual Studio](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&rel=16) C++ Build Tools
 - Open a terminal  
 - Run `pip install polymarket-trading`
 - Run `pm-trade -h` to display help

### Trading Setup
 - Create a new wallet on the matic chain
 - Create your matic RPC endpoint on https://rpc.maticvigil.com/ (or other RPC provider)
 - Set env variables
   - POLYGON_PRIVATE_KEY
   - MATIC_VIGIL_RPC_KEY or RPC_URI
 - Fund your trading wallet with matic and usdc

#### Made some money from this tool and want to contribute? Donate to these charities.
* [Planned Parenthood](https://www.weareplannedparenthood.org/onlineactions/2U7UN1iNhESWUfDs4gDPNg2)
* [Fair Fight](https://secure.actblue.com/donate/fair-fight-action--inc--1)
* [Brady Center to Prevent Gun Violence](https://www.bradyunited.org/donate/tax)
* [The Marshall Project](https://www.themarshallproject.org/donate)
