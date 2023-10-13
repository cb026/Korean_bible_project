    
"""
korean_bible.py

This module collect Korean bible verses from the "대한성서공회  웹사이트"
http://www.bskorea.or.kr

Author: CB Park
Date: Oct. 12, 2023
"""    

import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pprint import pprint
from tqdm import tqdm


BIBLES = [['01창세기', 'gen', '50'], ['02출애굽기', 'exo', '40'], ['03레위기', 'lev', '27'], 
 ['04민수기', 'num', '36'], ['05신명기', 'deu', '34'], ['06여호수아', 'jos', '24'], 
 ['07사사기', 'jdg', '21'], ['08룻기', 'rut', '4'], ['09사무엘상', '1sa', '31'], 
 ['10사무엘하', '2sa', '24'], ['11열왕기상', '1ki', '22'], ['12열왕기하', '2ki', '25'], 
 ['13역대상', '1ch', '29'], ['14역대하', '2ch', '36'], ['15에스라', 'ezr', '10'], 
 ['16느헤미야', 'neh', '13'], ['17에스더', 'est', '10'], ['18욥기', 'job', '42'], 
 ['19시편', 'psa', '150'], ['20잠언', 'pro', '31'], ['21전도서', 'ecc', '12'], 
 ['22아가', 'sng', '8'], ['23이사야', 'isa', '66'], ['24예레미야', 'jer', '52'], 
 ['25예레미야애가', 'lam', '5'], ['26에스겔', 'ezk', '48'], ['27다니엘', 'dan', '12'], 
 ['28호세아', 'hos', '14'], ['29요엘', 'jol', '3'], ['30아모스', 'amo', '9'],
 ['31오바댜', 'oba', '1'], ['32요나', 'jnh', '4'], ['33미가', 'mic', '7'], ['34나훔', 'nam', '3'], 
 ['35하박국', 'hab', '3'], ['36스바냐', 'zep', '3'], ['37학개', 'hag', '2'], 
 ['38스가랴', 'zec', '14'], ['39말라기', 'mal', '4'], ['40마태복음', 'mat', '28'],
 ['41마가복음', 'mrk', '16'], ['42누가복음', 'luk', '24'], ['43요한복음', 'jhn', '21'],
 ['44사도행전', 'act', '28'], ['45로마서', 'rom', '16'], ['46고린도전서', '1co', '16'],
 ['47고린도후서', '2co', '13'], ['48갈라디아서', 'gal', '6'], ['49에베소서', 'eph', '6'], 
 ['50빌립보서', 'php', '4'], ['51골로새서', 'col', '4'], ['52데살로니가전서', '1th', '5'],
 ['53데살로니가후서', '2th', '3'], ['54디모데전서', '1ti', '6'], ['55디모데후서', '2ti', '4'], 
 ['56디도서', 'tit', '3'], ['57빌레몬서', 'phm', '1'], ['58히브리서', 'heb', '13'],
 ['59야고보서', 'jas', '5'], ['60베드로전서', '1pe', '5'], ['61베드로후서', '2pe', '3'], 
 ['62요한1서', '1jn', '5'], ['63요한2서', '2jn', '1'], ['64요한3서', '3jn', '1'],
 ['65유다서', 'jud', '1'], ['66요한계시록', 'rev', '22']]

BIBLES = [ (bible[0], bible[1], int(bible[2])) for bible in BIBLES]
BASE_URL = 'http://www.bskorea.or.kr'
 

class KoreanBible():
        
    def get_chapter_url(self, book_en, chapter):
        url = f'{BASE_URL}/bible/korbibReadpage.php?version=HAN&book={book_en}&chap={chapter}'
        return url

    def get_soup(self, book_en, chapter):
        url = self.get_chapter_url( book_en=book_en, chapter=chapter)
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
        else:
            print(f'Error: {response.status_code}')
            soup = None
        return soup

    def get_bible_chapter_contents(self, book, book_en, chapter):
        soup = self.get_soup(book_en, chapter)
        if soup.find('font', class_='smallTitle'):
            small_title = soup.find('font', class_='smallTitle').text
        else:
            small_title = None
        idx = 0
        chap_df = pd.DataFrame(columns=['book','book_en','chapter', 'verse_no', 'verse', 'small_title' ])
        for item in tqdm(soup.find_all('span'), desc='get_bible_chapter_contents'):
            flag = False
            if item.find('span', class_='number'):
                num = item.find('span', class_='number').text
            text = item.text
            if text != num:
                if text == '성경 단어 검색':
                    flag = True
                    break
                else:
                    # print(text)
                    verse_num = text.split('\xa0\xa0\xa0')[0].strip()
                    verse = text.split('\xa0\xa0\xa0')[1].strip()
                    chap_df.loc[idx] = [book, book_en, chapter, num, verse, small_title ]
                    idx +=1
            if flag:
                break
        return  chap_df
    
    def parse_bible_meta_data(self, bible, verbose=True):
        if verbose: print(bible)
        book = bible[0]
        filename = f'{book}.csv'
        book_no = bible[0][ :2].strip()
        book_ko = bible[0][2: ].strip()
        book_en = bible[1].strip()
        max_chap_num = bible[2]
        if verbose: print(filename, book_no, book_ko,  book_en, max_chap_num)
        return filename, book_no, book_ko, book_en, max_chap_num

    def get_bible_book_contents(self, bible, path):
        filename, book_no, book_ko, book_en, max_chap_num = self.parse_bible_meta_data(
                                                                           bible, verbose=False)
        book_df = pd.DataFrame()
        for num in tqdm(range(max_chap_num), desc='get_bible_book_contents'):
            chapter = num + 1
            chap_df = self.get_bible_chapter_contents(book=book_ko, book_en=book_en, chapter=chapter)
            book_df = pd.concat([book_df, chap_df], ignore_index=True) 
        filepath = os.path.join(path, filename)
        book_df.to_csv(filepath, index=False)
        print(f'"{filepath}" is saved.')
        return book_df

    def get_all_bible_contents(self, bibles, path):
        for bible in tqdm(bibles, desc='get_all_bible_contents'):
            print(bible)
            self.get_bible_book_contents(bible, path)

    
def main():
    
    print(f'\n1.Collecting Bible Chapter Contents.')
    
#     # ['01창세기', 'gen', '50']
    bible = BIBLES[0]
    print(bible)

    kb = KoreanBible()
    chapter = 1
    filename, book_no, book_ko, book_en, max_chap_num = kb.parse_bible_meta_data(bible, 
                                                                                 verbose=False)
    soup = kb.get_soup(book_en, chapter)
    chap_num = soup.find('font', class_='chapNum').text
    small_title = soup.find('font', class_='smallTitle').text
    print(chap_num)
    print(small_title)
    
    df =  kb.get_bible_chapter_contents(book_ko, book_en, chapter)
    print(df.head(3))


    print(f'\n2.Collecting Bible Book Contents.')
    
    # ['06여호수아', 'jos', '24']
    bible = BIBLES[5]
    print(bible)
    kb = KoreanBible()
    filename, book_no, book_ko, book_en, max_chap_num = kb.parse_bible_meta_data(bible, 
                                                                                 verbose=False)
    # path = './data'
    path = r'D:\Korean_bible_project\data'
    book_df = kb.get_bible_book_contents(bible, path)
    print(book_df.info())
    

    print(f'\n3.Collecting All Bible Contents.')
    # CPU times: total: 1min 53s
    # Wall time: 31min 23s

#     path = '.\data'
#     kb = KoreanBible()
#     kb.get_all_bible_contents(BIBLES, path)

if __name__ == '__main__':
    main()
