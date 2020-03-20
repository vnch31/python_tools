import requests
import threading
import queue
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="url to brute force", required=True)
parser.add_argument("-w", "--wordlist", help="wordlist to use, defautl is common.txt", default='./common.txt')
parser.add_argument("-t", "--threads", help="number of threads", default=10)
parser.add_argument("-a", "--useragent", help="user-agent to use", default="Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0")
args = parser.parse_args()
target_url = args.url
wordlist_file = args.wordlist
threads  = args.threads
resume = None
user_agent = args.useragent


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
                    attempt_list.append(f"/{attempt}{ext}")

            for brute in attempt_list:
                url = target_url + brute
                sys.stdout.write('\033[K')
                print(url, end='\r')
                try:
                    headers = {}
                    headers['User-Agent'] = user_agent
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        print (f"[+][{response.status_code}] => {url}")

                except requests.HTTPError as e:
                    #if response.status_code != 404:                     
                    print ("[-][%d] => %s" % (e.code,url))                  
                    pass

    def print_banner():
        print('////////////////////////////////////////////////////////////////////////////')
        print('/////      ////  ////////////        ///////////////////////////////////////')
        print('////  ////  //////  //    //  ////////    ////  //    ////      ////    ////')
        print('///  ////  //  //    //////      //  ////  //    //////  ////////        ///')
        print('//  ////  //  //  ////////  //////  ////  //  ////////  ////////  //////////')
        print('/      ////  //  ////////  ////////    ////  //////////      ////      /////')
        print('////////////////////////////////////////////////////////////////////////////')
        print('///////////////////////////////////////////////////////////////////////////')
            
    print_banner()
    word_q = build_wordlist(wordlist_file)
    extensions = ['.php', '.bak']

    for i in range(threads):
        t = threading.Thread(target=dir_bruter, args=(word_q, extensions))
        t.start()
except KeyboardInterrupt:
    print('[-]Interrupting program')
    exit(1)



