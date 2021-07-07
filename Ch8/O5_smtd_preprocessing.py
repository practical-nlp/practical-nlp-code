'''
Contains helper funtions for preprocessing of twitter documents before getting their corresponding vectors
from word2vec_twitter model

Author: Anuj Gupta
'''

'''
functionality:

Discard non-english tweets
Discard Replies
Discard RTs
For now this is handle while fetch tweet text from mongo documents

process constantbrands mentions
process any other mentions
process constant brand name if any 

process hanstags
process URLs
process websites
process process_EmailIds

process 

process alphanums
'''

import re
import string
import demoji
demoji.download_codes()
from nltk.tokenize import TweetTokenizer

# Global

PunctChars = r'''[`'“".?!,:;]'''
Punct = '%s+' % PunctChars
Entity = '&(amp|lt|gt|quot);'
printable = set(string.printable)

# Helper functoins.

def regex_or(*items):
	r = '|'.join(items)
	r = '(' + r + ')'
	return r

def pos_lookahead(r):
	return '(?=' + r + ')'

def neg_lookahead(r):
	return '(?!' + r + ')'

def optional(r):
	return '(%s)?' % r

def trim(transient_tweet_text):

	''' 
	trim leading and trailing spaces in the tweet text
	'''
	return transient_tweet_text.strip()

def strip_whiteSpaces(transient_tweet_text):
	'''
	Strip all white spaces
	'''
	transient_tweet_text = re.sub(r'[\s]+', ' ', transient_tweet_text)
	return transient_tweet_text

def to_LowerCase(transient_tweet_text):
	'''
	Convert tweet text to lower to lower case alphabets
	'''
	transient_tweet_text = transient_tweet_text.lower()
	return transient_tweet_text

def prune_multple_consecutive_same_char(transient_tweet_text):
	'''
	yesssssssss  is converted to yess 
	ssssssssssh is converted to ssh
	'''
	transient_tweet_text = re.sub(r'(.)\1+', r'\1\1', transient_tweet_text)
	return transient_tweet_text

def remove_spl_words(transient_tweet_text):
	transient_tweet_text = transient_tweet_text.replace('&amp;',' and ')

	return transient_tweet_text

def strip_unicode(transient_tweet_text):
    '''
    Strip all unicode characters from a tweet
    '''
    tweet = ''.join(i for i in transient_tweet_text if ord(i)<128)
    return tweet 

def process_URLs(transient_tweet_text):
	'''
	replace all URLs in the tweet text
	'''
	UrlStart1 = regex_or('https?://', r'www\.',r'bit.ly/')
	CommonTLDs = regex_or('com','co\\.uk','org','net','info','ca','biz','info','edu','in','au')
	UrlStart2 = r'[a-z0-9\.-]+?' + r'\.' + CommonTLDs + pos_lookahead(r'[/ \W\b]')
	UrlBody = r'[^ \t\r\n<>]*?'  # * not + for case of:  "go to bla.com." -- don't want period
	UrlExtraCrapBeforeEnd = '%s+?' % regex_or(PunctChars, Entity)
	UrlEnd = regex_or( r'\.\.+', r'[<>]', r'\s', '$')
	Url = 	(optional(r'\b') + 
    		regex_or(UrlStart1, UrlStart2) + 
    		UrlBody + 
    pos_lookahead( optional(UrlExtraCrapBeforeEnd) + UrlEnd))

	Url_RE = re.compile("(%s)" % Url, re.U|re.I)
	transient_tweet_text = re.sub(Url_RE, " constanturl ", transient_tweet_text)

	# Fix to handle unicodes in URL.

	URL_regex2 = r'\b(htt)[p\:\/]*([\\x\\u][a-z0-9]*)*'
	transient_tweet_text = re.sub(URL_regex2, " constanturl ", transient_tweet_text)
	return transient_tweet_text

def process_Websites(transient_tweet_text):
	'''
	identify website mentioned if any 
	'''
	CommonTLDs = regex_or('com','co\\.uk','org','net','info','ca','biz','info','edu','in','au')
	sep = r'[.]'
	website_regex = r'(?<!#)?(\b)?[a-zA-Z0-9.]+' + sep + CommonTLDs
	website_RE = re.compile("(%s)" % website_regex, re.U|re.I)
	transient_tweet_text = re.sub(website_RE, ' constantwebsite ', transient_tweet_text)

	return transient_tweet_text

def process_EmailIds(transient_tweet_text):
	'''
	identify email mentioned if any
	'''
	email_regex = r'(\b)?[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(\b)?'
	transient_tweet_text = re.sub(email_regex, ' constantemailid ', transient_tweet_text)

	return transient_tweet_text

def process_Mentions(transient_tweet_text):
	'''
	Identify mentions if any
	'''
	transient_tweet_text = re.sub(r"@(\w+)", " constantnonbrandmention ", transient_tweet_text)
	return transient_tweet_text
def process_HashTags(transient_tweet_text):
	'''
	Strip all Hashtags from a tweet
	'''
	transient_tweet_text = re.sub(r"#(\w+)\b", ' constanthashtag ', transient_tweet_text)
	return transient_tweet_text

def process_Dates(transient_tweet_text):
	'''
	Identify date and convert it to constant
	'''
	# transient_tweet_text = re.sub(r'(\d+/\d+/\d+)', " constantdate " , transient_tweet_text)
	# transient_tweet_text = re.sub(r'constantnum[\s]?(/|-)[\s]?constantnum[\s]?(/|-)[\s]?constantnum', " constantdate " , transient_tweet_text)
	# date_regex = r'(constantnum)[\s]*(st|nd|rd|th)[\s]*(january|jan|february|feb|march|mar|april|may|june|jun|july|august|aug|september|sep|october|oct|november|nov|december|dec)'
	date_regex1 = r'\b((0|1|2|3)?[0-9][\s]*)[-./]([\s]*([012]?[0-9])[\s]*)([-./]([\s]*(19|20)[0-9][0-9]))?\b'
	transient_tweet_text = re.sub(date_regex1, ' constantdate ' , transient_tweet_text)
	date_regex2 = r'\b((19|20)[0-9][0-9][\s]*[-./]?)?[\s]*([012]?[0-9])[\s]*[-./][\s]*(0|1|2|3)?[0-9]\b'
	transient_tweet_text = re.sub(date_regex2, ' constantdate ' , transient_tweet_text)

	Months = regex_or('january','jan','february','feb','march','mar','april','may','june','jun','july','jul','august','aug','september','sep','october','oct','november','nov','december','dec')
	date_regex3 = r'\d+[\s]*(st|nd|rd|th)[\s]*' + Months 
	transient_tweet_text = re.sub(date_regex3, ' constantdate ', transient_tweet_text)
	date_regex4 = Months + r'[\s]*\d+[\s]*(st|nd|rd|th)*\b'
	transient_tweet_text = re.sub(date_regex4, ' constantdate ' , transient_tweet_text)
	date_regex5 = r'[\s]?\b(19|20)[0-9][0-9]\b[\s]?'
	transient_tweet_text = re.sub(date_regex5, ' constantdate ' , transient_tweet_text)

	date_regex6 = r'([\s]*(constantdate))+'
	transient_tweet_text = re.sub(date_regex6, ' constantdate ' , transient_tweet_text)

	return transient_tweet_text

def process_Times(transient_tweet_text):
	'''
	Indentify time and convert it to constant
	'''
	time_regex1 = r'([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9][\s]*(am|pm)?[\s]*([iescm](st)|gmt|utc|[pmce](dt))?'
	transient_tweet_text = re.sub(time_regex1, ' constanttime ' , transient_tweet_text)

	return transient_tweet_text

def process_BrandMentions(transient_tweet_text):
	'''
	process all airrwoot brands Mentions if any in tweet text
	'''
	constant_brands = regex_or('paytmcare', 'paytm','snapdeal_help','snapdeal','bluestone_com','shopohelp','shopo','mobikwikswat',
		'mobikwik','taxiforsure','tfscares','zoomcarindia','freshmenuindia','freshmenucares','grofers','jetairways',
		'cleartrip','olacabs','support_ola','makemytrip','makemytripcare','chai_point')

	BrandMentionRegex = r'@(\b)*' + constant_brands
	transient_tweet_text = re.sub(BrandMentionRegex, ' constantbrandmention ', transient_tweet_text)
	return transient_tweet_text

def process_NonBrandMentions(transient_tweet_text):
	'''
	process all Mentions left, if any, in tweet text
	'''
	transient_tweet_text = re.sub(r"@(\w+)", ' constantnonbrandmention ', transient_tweet_text)
	return transient_tweet_text

def process_BrandName(transient_tweet_text):
	'''
	process all airrwoot brands Mentions if any in tweet text
	'''
	constant_brands = regex_or('paytmcare', 'paytm','snapdeal_help','snapdeal','bluestone_com', 'bluestone','shopohelp','shopo',
		'mobikwikswat','mobikwik','taxiforsure','tfscares', 'tfs','zoomcarindia', 'zoomcar','freshmenuindia','freshmenucares', 
		'freshmenu','grofers','jetairways', 'jet','cleartrip','olacabs','support_ola', 'olacab', 'ola' ,'makemytrip',
		'makemytripcare', 'chai_point')

	BrandNameRegex = constant_brands
	transient_tweet_text = re.sub(BrandNameRegex, ' constantbrandname ', transient_tweet_text)
	return transient_tweet_text

def identify_Savings(transient_tweet_text):
	'''
	identify sale/save offers
	'''
	# sale_regex = r'(?<!#)\b(discount|discounts|sale|save|saver|super[\s]*saver|super[\s]*save)\b[\s]*(constantnum)*[\s]*[%]?[\s]*(-|~)?[\s]*(constantnum)*[\s]*[%]?'
	sale_regex = r'(?<!#)\b(discount|discounts|sale|save|saver|super[\s]*saver|super[\s]*save)\b[\s]*((rs|\$)*[\s]*(constantnum))*[\s]*[%]?[\s]*(-|~|or)?[\s]*((rs|\$)*[\s]*(constantnum))*[\s]*[%]?'
	transient_tweet_text = re.sub(sale_regex, " constantdiscount ", transient_tweet_text)
	# discount_List = []
	# discount_List = re.findall(r'constantdiscount', transient_tweet_text)
	return transient_tweet_text

def indentify_Offers(transient_tweet_text):
	'''
	identify cashbacks and off / substrings of the form "30% off" or "30% cashback" or "$30 off"
	Replace them by constantOFFER
	'''
	# transient_tweet_text = re.sub(r'[rs|$]?[ ]*[constantnum][ ]*[%]?[ ]?[off|cashback|offer]', "constantoffer", transient_tweet_text)
	transient_tweet_text = re.sub(r'(?<!#)\b(?:(up[\s]?to)?((rs|\$)*[\s]*(constantnum))[\s]*[%]?)?[\s]*[-|~|or]?[\.]?[\s]*((rs|\$)*[\s]*(constantnum))*[\s]*[%]?[\s]*(offer|off|cashback|cash|cash back)', " constantoffer ", transient_tweet_text)
	transient_tweet_text = re.sub(r'(?<!#)\b(?:cashback|cash back|cash)\b', " constantoffer ", transient_tweet_text)
	# Offer_List = []
	# Offer_List = re.findall(r'constantoffer', transient_tweet_text)
	return transient_tweet_text

def indentify_Promos(transient_tweet_text):
	'''
	indentify coupons/promos with promo codes
	Assumption - promo code can be alphanumeric. But it immediately follows text of promo/code/promocode etc
	'''
	# transient_tweet_text = re.sub(r'\b(promocode|promo code|promo|code)[s]?[\s]*[a-z]*(constantnum)*[a-z]*[\s]+', " constantpromo ", transient_tweet_text)
	transient_tweet_text = re.sub(r'(?<!#)\b(?:promocode|promo code|promo|coupon code|code)\b[\s]*(constantalphanum)\b', " constantpromo ", transient_tweet_text)
	transient_tweet_text = re.sub(r'(?<!#)\b(?:promocode|promo code|promo|coupon code|code)\b[\s]*[a-z]+\b', " constantpromo ", transient_tweet_text)
	transient_tweet_text = re.sub(r'(?<!#)\b(?:promocode|promo code|promo|coupon code|code)\b[\s]*[0-9]+\b', " constantpromo ", transient_tweet_text)
	transient_tweet_text = re.sub(r'(?<!#)\b(?:promocode|promo code|promo|coupon code|code|coupon)[s]?\b', " constantpromo ", transient_tweet_text)
	# Promo_List = []
	# Promo_List = re.findall(r'constantpromo', transient_tweet_text)
	return transient_tweet_text

def indentify_Money(transient_tweet_text):
	'''
	identify money in the tweet text but outside offers. This includes $,Rs, pound, Euro
	'''
	money_regex1 = r'\b(rs|\$)[\s]*(constantnum)?[\.]?[\s]*constantnum\b'
	transient_tweet_text = re.sub(money_regex1, " constantmoney ", transient_tweet_text)
	money_regex2 = r'[\s]*[\.]?[\s]*constantnum(cent[s]?|\$|c)\b'
	transient_tweet_text = re.sub(money_regex2, " constantmoney ", transient_tweet_text)
	money_regex3 = r'(\$|rs)[\s]*constantalphanum'
	transient_tweet_text = re.sub(money_regex3, " constantmoney ", transient_tweet_text)
	# Money_List = []
	# Money_List = re.findall(r'constantmoney', transient_tweet_text)
	return transient_tweet_text

def indentify_freebies(transient_tweet_text):
	'''
	indentify freebies in tweets if any - free offers, free shipping, free trial, 
	'''
	freebies_regex1 = r'(?<!#)\b(?:free)[\s]+[a-z]+\b'
	transient_tweet_text = re.sub(freebies_regex1, " constantfreebies ", transient_tweet_text)
	freebies_regex2 = r'(?<!#)\b(?:free)[\s]+[a-z]*\b'
	transient_tweet_text = re.sub(freebies_regex2, " constantfreebies ", transient_tweet_text)
	return transient_tweet_text

def replace_numbers(transient_tweet_text):
	'''
	Given any number/interger in tweet text, we want it to be replaced by constantnum
	'''
	# we want to process only those numbers that are not in a hashtag - below logic does this
	num_regex = r'(?<!#)\b(?:[-+]?[\d,]*[\.]?[\d,]*[\d]+|\d+)\b'
	transient_tweet_text = re.sub(num_regex, " constantnum " , transient_tweet_text)
	return transient_tweet_text

def identify_AlphaNumerics(transient_tweet_text):
	'''
	Identify alpha numerics - this helps in identifying product codes/models, promocodes, Order IDs
	'''
	AlphaNumeric_regex = r'(?<!#)\b(?:([a-z]+[0-9]+[a-z]*|[a-z]*[0-9]+[a-z]+)[a-z,0-9]*)\b'
	transient_tweet_text = re.sub(AlphaNumeric_regex, " constantalphanum ", transient_tweet_text)
	return transient_tweet_text

def strip_whiteSpaces(transient_tweet_text):
	'''
	Strip all white spaces
	'''
	transient_tweet_text = re.sub(r'[\s]+', ' ', transient_tweet_text)
	return transient_tweet_text

def prune_multple_consecutive_same_char(transient_tweet_text):
	'''
	yesssssssss  is converted to yess 
	ssssssssssh is converted to ssh
	'''
	transient_tweet_text = re.sub(r'(.)\1+', r'\1\1', transient_tweet_text)
	return transient_tweet_text

def remove_spl_words(transient_tweet_text):
	transient_tweet_text = transient_tweet_text.replace('&amp;',' and ')

	return transient_tweet_text

def remove_emoji(transient_tweet_text):
    '''
    replace emoji with the respective emotion
    '''
    tweet_tokenizer = TweetTokenizer()
    tokenized_tweet = tweet_tokenizer.tokenize(transient_tweet_text)
    emojis_present = demoji.findall(transient_tweet_text)
    tweet_no_emoji=''
    for i,s in enumerate(tokenized_tweet):
        if s in emojis_present.keys():
            tweet_no_emoji = tweet_no_emoji + ' ' + emojis_present[s]
        else:
            tweet_no_emoji = tweet_no_emoji + ' ' + s
    return tweet_no_emoji

def deEmojify(transient_tweet_text):
    '''
    remove all emojis which were not replaced by their respective emotion
    '''
    return transient_tweet_text.encode('ascii', 'ignore').decode('ascii')

# def print_test():
    
#     test_tweet = "Nice @varun paytm @paytm saver abc@gmail.com sizes for the wolf on 20/10/2010 at 10:00PM  grey/deep royal-volt Nike Air Skylon II retro are 40% OFF for a limited time at $59.99 + FREE shipping.BUY HERE -> https://bit.ly/2L2n7rB (promotion - use code MEMDAYSV at checkout)"
#     #General Proprocessing
#     test_tweet = test_tweet.lower()
#     test_tweet = strip_unicode(test_tweet)
    
#     #function tests
#     print("Process URLS:\n",process_URLs(test_tweet))
#     print("Remove websites:\n",process_Websites(test_tweet))
#     print("Remove mentions:\n",process_Mentions(test_tweet))
#     print('Remove Emailid:\n',process_EmailIds(test_tweet))
#     print("Remove Hashtags:\n",process_HashTags(test_tweet))
#     print("Remove Dates:\n",process_Dates(test_tweet))
#     print("Process Time:\n",process_Times(test_tweet))
#     print("Process Brand Mention:\n",process_BrandMentions(test_tweet))
#     print("Process non Brand Mention:\n",process_NonBrandMentions(test_tweet))
#     print("Process Brand Name:\n",process_BrandName(test_tweet))
#     print("Process Savings:\n",identify_Savings(test_tweet))
#     print("Process Offers:\n",indentify_Offers(test_tweet))
#     print("Identiy Promos:\n",indentify_Promos(test_tweet))
# ############
# print_test()

def process_TweetText(tweet_text):
	'''
	Takes tweet_text and preprocesses it 

	Order of preprocessing:

	'''

	# get utf-8 encoding, lowercase, trim and remove multiple white spaces
	
	transient_tweet_text = tweet_text
	transient_tweet_text = strip_unicode(transient_tweet_text)
	
	# print "PROCESSED: ", transient_tweet_text

	transient_tweet_text = to_LowerCase(transient_tweet_text)
	transient_tweet_text = trim(transient_tweet_text)
	transient_tweet_text = strip_whiteSpaces(transient_tweet_text)
	transient_tweet_text = remove_spl_words(transient_tweet_text)

	# Emoji
	
	transient_tweet_text = remove_emoji(transient_tweet_text) 
	transient_tweet_text = deEmojify(transient_tweet_text)
	
	# Process Hastags, URLs, Websites, process_EmailIds
	# Give precedence to url over hashtag
	
	transient_tweet_text = process_URLs(transient_tweet_text)
	transient_tweet_text = process_HashTags(transient_tweet_text)
	
	# transient_tweet_text = process_Websites(transient_tweet_text)
	
	transient_tweet_text = process_EmailIds(transient_tweet_text)

	# Process for brand mention, any other mention and brand Name
	# transient_tweet_text = process_BrandMentions(transient_tweet_text)
	# transient_tweet_text = process_NonBrandMentions(transient_tweet_text)
	transient_tweet_text = process_Mentions(transient_tweet_text)
	#transient_tweet_text = process_BrandName(transient_tweet_text)

	# Remove any unicodes
	transient_tweet_text = strip_unicode(transient_tweet_text)

	# Identify Date / Time if any
	transient_tweet_text = process_Times(transient_tweet_text)
	transient_tweet_text = process_Dates(transient_tweet_text)

	# Identify alphanums and nums
	transient_tweet_text = identify_AlphaNumerics(transient_tweet_text)
	transient_tweet_text = replace_numbers(transient_tweet_text)
	
	# Identify promos, savings, offers, money and freebies
	transient_tweet_text = indentify_Promos(transient_tweet_text)
	transient_tweet_text = identify_Savings(transient_tweet_text)
	transient_tweet_text = indentify_Offers(transient_tweet_text)
	transient_tweet_text = indentify_Money(transient_tweet_text)
	transient_tweet_text = indentify_freebies(transient_tweet_text)

	transient_tweet_text = trim(transient_tweet_text)
	transient_tweet_text = strip_whiteSpaces(transient_tweet_text)

	transient_tweet_text = prune_multple_consecutive_same_char(transient_tweet_text)

	return transient_tweet_text

# if __name__ == "__main__":
#	print(process_TweetText("Nice @varun paytm @paytm saver abc@gmail.com sizes for the wolf on 20/10/2010 at 10:00PM  grey/deep royal-volt Nike Air Skylon II retro are 40% OFF for a limited time at $59.99 + FREE shipping.BUY HERE -> https://bit.ly/2L2n7rB (promotion - use code MEMDAYSV at checkout)"))