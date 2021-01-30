


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">References</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
This is a CLI tool that downloads files from the BitTorrent network.

I wanted to make a straightforward program to learn how does BitTorrent protocol works.

It is written with python 3.8, only the pubsub library was used to create events when a new peer is connected, or when data is received from a peer. You first need to wait for the program to connect to some peers first, then it starts downloading.

With this torrent client, you can :

<li>Read a torrent file</li>
<li>Scrape udp or http trackers</li>
<li>Connect to peers</li>
<li>Ask them for the blocks you want</li>
<li>Save a block in RAM, and when a piece is completed and checked, write the data into your hard drive</li>


### Built With
Python


<!-- GETTING STARTED -->
## Getting Started


### Prerequisites
1. Python
2. Knowledge of TCP/UDP protocols
3. Asynchronous programming 
4. Peer to Peer networks

### Installation
You can run the following command to install the dependencies using pip

pip3 install -r requirements.txt<br>
**Note**:This is not applicable on Windows



<!-- USAGE EXAMPLES -->
## Usage

If you want to specify a torrent file, you need to edit it manually in the main.py file:  
``` python
self.torrent = Torrent.Torrent("path_to_your_torrent") 
```
Then simply run:
`python3 main.py`

The files will be downloaded in the same path as your main.py script.






<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/Torrent-Client`)
3. Commit your Changes (`git commit -m 'Add some features'`)
4. Push to the Branch (`git push origin feature/Torrent-Client`)
5. Open a Pull Request



<!-- CONTACT -->
## Contact
Name : Adriraj Chaudhuri<br>
Email : adriraj@itg.ac.in


<!-- REFERENCES -->
## References
1.http://allenkim67.github.io/programming/2016/05/04/how-to-make-your-own-bittorrent-client.html<br>
2.http://www.kristenwidman.com/blog/33/how-to-write-a-bittorrent-client-part-1/<br>
3.https://github.com/gallexis/pytorrent<br>
4.https://github.com/lita/bittorrent<br>
5.https://wiki.theory.org/BitTorrentSpecification


