import urllib
import re
import sys
import os
import time

def retrivePagesFromGallary(gallaryUrl):
    html = urllib.urlopen(gallaryUrl).read()
    pageCount = getGallaryPageCount(html)
    urls = extractPageUrls(html)
    for i in range(1, pageCount-1):
        html = urllib.urlopen(gallaryUrl + '?p=' + str(i)).read()
        urls += extractPageUrls(html)
    return urls

def getGallaryPageCount(html):
     targetTable = extractInfo(html, '<table class="ptt".*?</table>')
     return countTdTagInHtml(targetTable) - 2

def getGallaryTitle(html):
    targetDiv = extractInfo(html, '<h1 id="gn">.*?</h1>')
    return targetDiv[12:].split("<")[0]

def extractPageUrls(gallaryHtml):
    pattern = re.compile(r'<div class="gdtm".*?</a>', re.S)
    allDiv = pattern.findall(gallaryHtml)
    urls = []
    for div in allDiv:
        aTag = extractInfo(div, "<a href=.*?>")
        urls.append(aTag.split('"')[1])
    return urls

def countTdTagInHtml(html):
    pattern = re.compile(r'<td.*?>', re.S)
    allTd = pattern.findall(html)
    return len(allTd)

def downloadPictureFromPage(pageUrl, basePath = ''):
    imgUrl = retrivePictureUrl(pageUrl)
    print 'Downloading ' + retriveFilename(imgUrl) + ' ' + '...'
    downloadPicture(imgUrl, basePath)

def retrivePictureUrl(url):
    html = urllib.urlopen(url).read()
    targetImgTag = extractInfo(html, '<img id=.*?>')
    return targetImgTag.split('"')[3]

def extractInfo(content, regExp):
    pattern = re.compile(regExp, re.S)
    match = pattern.search(content)
    if match :
        return match.group()
    else:
        return ''

def downloadPicture(url, basepath = ''):
    if basepath != '' and basepath[-1] != '/':
        fileName = basepath + '/' + retriveFilename(url)
    else:
        fileName = basepath + retriveFilename(url)
    urllib.urlretrieve(url, fileName)

def retriveFilename(url):
    tokens = url.split('/')
    return tokens[-1]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage : python main.py <url>"
        sys.exit()
    
    gallaryUrl = sys.argv[1]
    html = urllib.urlopen(sys.argv[1]).read()
    gallaryTitle = getGallaryTitle(html)
    os.mkdir(gallaryTitle)
    pageUrls = retrivePagesFromGallary(sys.argv[1])
    for page in pageUrls:
        downloadPictureFromPage(page, gallaryTitle)
        time.sleep(1)

def denoising_tuning(data, 
                     wavelets = [i for i in pywt.wavelist() if i not in ['shan','morl','mexh','fbsp','cmor','cgau1',
                                                                         'cgau2','cgau3','cgau4','cgau5','cgau6','cgau7',
                                                                         'cgau8','gaus1','gaus2','gaus3','gaus4','gaus5',
                                                                         'gaus6','gaus7','gaus8']],
                     mode_thresh = ['hard', 'less'],
                     mode_dec_reb_wave = ['symmetric', 'periodic', 
                                          'smooth', 'periodization', 'reflect', 
                                          'antisymmetric', 'antireflect']):
    '''
    denoises data according to different combinations of wavelets, 
    thresholding techniques and wave rebuilding techniques
    returns signals-params ordered by NRMSE
    '''
    if len(np.unique(data)) <= 5:
        return data

    denoised = []
    #for wd, i in zip(wavelets_dec, tqdm(range(len(wavelets_dec)))):
    error = np.inf
    temp_params = {}
    for wavelet in wavelets:
    #for wavelet, jjj in zip(wavelets, range(1, len(wavelets) + 1)):
        #print('Testing wavelet {} of {}'.format(jjj, len(wavelets)))
        for mt in mode_thresh:
            for mdrw in mode_dec_reb_wave:
                temp = denoise_signal(data, level = 1, 
                                      wavelet = wavelet,
                                      mode_thresh = mt, 
                                      mode_dec_reb_wave = mdrw)
                
                if len(np.unique(temp)) <= 5:
                    continue

                if len(temp) > len(data):
                    temp = temp[ : -1]

                temp_err = NRMSE(data, temp)
                if temp_err < error:
                    temp_params = {'wavelet': wavelet, 'mode_thresh': mt, 'mode_dec_reb_wave': mdrw}
                    error = temp_err

    denoised_signal = denoise_signal(data, level = 1, 
                                     wavelet = temp_params['wavelet'],
                                     mode_thresh = temp_params['mode_thresh'], 
                                     mode_dec_reb_wave = temp_params['mode_dec_reb_wave'])
    #return sorted(denoised, key = itemgetter('NRMSE')) 
    return denoised_signal