import urllib3
import threading
import queue
import argparse
import sys
import signal

""" Argument parser """
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="url to brute force", required=True)
parser.add_argument("-w", "--wordlist", help="wordlist to use, defautl is common.txt", default='./common.txt')
parser.add_argument("-t", "--threads", help="number of threads", default=10)
parser.add_argument("-a", "--useragent", help="user-agent to use", default="Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0")
parser.add_argument("-e", "--extensions", help="Extensions lists", nargs="+")
args = parser.parse_args()
if args.url.endswith('/'):
    target_url = args.url.rstrip('/')
else:
    target_url = args.url
wordlist_file = args.wordlist
threads  = args.threads
resume = None
user_agent = args.useragent
threads_list = []

""" Handle control-c """
def signal_handler(signal, frame):
    for thread in threads_list:
        thread.kill_received = True
    print(f"\n {bcolors.BOLD}Exiting program...{bcolors.ENDC}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

""" Colors """
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

""" urllib3 """
http = urllib3.PoolManager()

try:

    def build_wordlist(wordlist_file):
        # read the wordlist file
        fd = open(wordlist_file, 'rb')
        raw_words = fd.readlines()
        fd.close()
        found_resume = False
        words = queue.Queue()

        for word in raw_words:
            word = word.rstrip()
            if resume is not None:
                if found_resume:
                    words.put(word)
                else:
                    if word == resume:
                        found_resume = True
                        print (f"[?]Resuming wordlist from {resume}")
            else:
                words.put(word)
        return words

    def dir_bruter(word_queue, extensions=None):
        while not word_queue.empty():
            attempt = str(word_queue.get(), 'utf-8')

            attempt_list = []

            # check if there is a file extension if not it's a directory
            if '.' not in str(attempt):
                attempt_list.append(f"/{attempt}/")
            else:
                attempt_list.append(f"/{attempt}")

            # if extensions is given
            if extensions:
                for ext in extensions:
                    attempt_list.append(f"/{attempt}.{ext}")

            for brute in attempt_list:
                url = target_url + brute
                sys.stdout.write('\033[K')
                print(url, end='\r')
                try:
                    headers = {}    
                    headers['User-Agent'] = user_agent
                    r = http.request('GET', url, headers=headers)
                    r_headers = dict(r.headers)
                    try:
                        content_length = r_headers['Content-Length']
                    except KeyError:
                        content_length = "?"
                    if r.status == 200:
                        print (f"{bcolors.OKGREEN}[{r.status}]{bcolors.ENDC} - {content_length} KB => {url}")
                    elif r.status == 302:
                        r = http.request('GET', url, headers=headers, redirect=True)
                        print (f"{bcolors.WARNING}[{r.status}]{bcolors.ENDC} - {content_length} KB => {url} redirect to => {r.geturl()} ")
                    elif r.status != 404:
                        print (f"{bcolors.WARNING}[{r.status}]{bcolors.ENDC} - {content_length} KB  => {url}")

                except urllib3.exceptions.HTTPError as e:
                    if r.status != 404:                     
                        print (f"{bcolors.FAIL}[{e.code}]{bcolors.ENDC} =>{url}")                  
                    pass

    def print_banner():
        print("\n")
        print('////////////////////////////////////////////////////////////////////////////')
        print('/////      ////  ////////////        ///////////////////////////////////////')
        print('////  ////  //////  //    //  ////////    ////  //    ////      ////    ////')
        print('///  ////  //  //    //////      //  ////  //    //////  ////////        ///')
        print('//  ////  //  //  ////////  //////  ////  //  ////////  ////////  //////////')
        print('/      ////  //  ////////  ////////    ////  //////////      ////      /////')
        print('////////////////////////////////////////////////////////////////////////////')
        print('///////////////////////////////////////////////////////////////////////////')
        print("\n")
            
    print_banner()
    word_q = build_wordlist(wordlist_file)
    print(f'{bcolors.OKBLUE}[+]{word_q.qsize()}{bcolors.ENDC} words to test : ')
    if args.extensions:
        extensions = args.extensions
    else:
        extensions = ['html']
    for i in range(threads):
        t = threading.Thread(target=dir_bruter, args=(word_q, extensions))
        t.start()
        threads_list.append(t)
except:
    print(f"{bcolors.FAIL}[-] An error occured{bcolors.ENDC}")
    exit(1)



