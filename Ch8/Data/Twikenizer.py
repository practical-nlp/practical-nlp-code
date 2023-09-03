import re, emoji

def get_emoji_regexp():
    emoji_data = emoji.EMOJI_DATA.keys()
    emoji_pattern = re.compile('|'.join(re.escape(emoji) for emoji in emoji_data))
    return emoji_pattern


class Twikenizer():

    def __init__(self):
        
        '''
        Symbols regex
          - Punctuation marks: ,.;:?!
          - Parenthesis: ()[]{}
          - Quotes: "'
          - Others: -
        
        Emojies regex
          - All unicode emojies
        
        Special characters regex
          - %$&€#~º+^<>|\£§¬/
        '''

        # Initializing regular expressions
        self.symbols_regex = r'["\'.!?,;:\()\[\]\{\}_-]'
        self.emojies_regex = get_emoji_regexp()
        self.special_chars_regex = r'^[%$&€#@~º+\^<>|\\£§¬\/]+$'
        self.other_inv_chars_regex = r'[%$&€#@~º+\^<>|\\£§¬\/]'
        self.invalid_hashtags_mentions_chars = r'["\'.!?,;:\()\[\]\{\}%$&€#@~º+\^<>|\\£§¬\/-]'
        

    def tokenize(self, tweet):

        '''
        Transforms a lists of raw tokens (whitespace separated) into a 
        list of processed tokens using predefined metrics 
        '''

        # Splitting first by whitespace
        raw_tokens = tweet.split()
        
        # Initializing list of final tokens
        tokens = []
        
        for raw_token in raw_tokens:

            # Initializing auxiliar variables
            subtokens, substring = [], ''

            '''
            First, we handle hashtags and mentions
            '''

            # Getting first character of the raw token
            first_char = raw_token[0]
            len_raw_token = len(raw_token)

            # Looking for valid hashtags
            if first_char == '#' and len_raw_token > 1:
                # Parsing raw token
                subtokens, valid_hashtag = self.parse_hashtags_mentions(raw_token)
                # Hashtag is fully valid - no more parsing needed
                if valid_hashtag == 1:
                    tokens += subtokens
                    continue
                # Left hand side of the hashtag is valid - right hands side needs parsing
                elif valid_hashtag == 0:
                    tokens.append(subtokens[0])
                    raw_token = subtokens[1]
            
            # Looking for valid mentions
            elif first_char == '@' and len_raw_token > 1:
                # Parsing raw token
                subtokens, valid_mention = self.parse_hashtags_mentions(raw_token, False)
                # Mention is fully valid - no more parsing needed
                if valid_mention == 1:
                    # Hashtag or mention handled correctly, nothing else to parse
                    tokens += subtokens
                    continue
                # Left hand side of the mention is valid - right hands side needs parsing
                elif valid_mention == 0:
                    # Hashtag or mention handled correctly, parse right hand side
                    tokens.append(subtokens[0])
                    raw_token = subtokens[1]
            
            '''
            - Valid hashtags and mentions have been handled.
            - Invalid hashtags and mentions and respective invalid right hand sides are parsed as any other raw token
                e.g. #hashtag       - Fully parsed at this point
                     #hashtag.lol   - Left hand side parsed (#hashtag), right hand side is parsed as any other token (.lol) 
                     #$hashtag      - Invalid hashtag, parsed as a whole raw token (#$hashtag)

            - Now parsing the rest of the raw tokens
            '''

            # Initializing lists characters found per raw token
            symbols = re.findall(self.symbols_regex, raw_token)
            specials = re.findall(self.other_inv_chars_regex, raw_token)
            emojies = re.findall(self.emojies_regex, raw_token)
            special_chars = re.findall(self.special_chars_regex, raw_token)


            if (symbols and specials) or (symbols and specials and emojies) or (emojies and specials) or (emojies and symbols):
                subtokens = self.parser(raw_token, r'[a-zA-Z0-9]', True)
            # Parsing strings containing only symbols and alphanumerics
            elif symbols:
                subtokens = self.parser(raw_token, self.symbols_regex)
            # Parsing strings containing only emojies and alphanumerics
            elif emojies:
                subtokens = self.parser(raw_token, self.emojies_regex)
            # Parsing strings containing only special characters
            elif special_chars:
                subtokens += raw_token
            # Parsing alphanumeric tokens
            else:
                #print('5subtokens', subtokens)
                subtokens.append(raw_token)
                #print('5subtokens', subtokens)

            # Merging tokens
            tokens += subtokens

        return tokens


    def parser(self, raw_token, regex, general=False):

        '''
        - General parser -
        Parses any raw token that isn't a valid hashtag or mention
        '''
        
        # Initializing auxiliar variables
        subtokens, substring, position = [], '', 0  

        # Processing each character individually
        for char in raw_token:

            # 'General' includes all possible combinations of emojies, special characters
            # and symbols (plus alphanumeric) characters
            if general:
                # Found alphanumeric character
                if re.match(regex, char):
                    substring += char
                    # Appending substring if this is the last position of the raw token
                    if position == len(raw_token) - 1 and substring:
                        subtokens.append(substring)
                # Found an emoji, special char or symbol
                else:
                    # Appending constructed substring before handling character
                    if substring: 
                        subtokens.append(substring)
                    # If symbol, append substring to the tokens list
                    substring = '' # Reset substring after appending
                    subtokens.append(char) # Appending to tokens symbol char indivually

            # Raw token containg only alphanumeric characters plus symbols, emojies or special characters
            # Or only special characters
            else:
                # Found alphanumeric character
                if not re.match(regex, char): 
                    substring += char
                    # Appending substring if this is the last position of the raw token
                    if position == len(raw_token) - 1 and substring:
                        subtokens.append(substring)
                # Found an emoji, special char or symbol
                else:
                    # Appending constructed substring before handling character
                    if substring: 
                        subtokens.append(substring)
                    # If symbol, append substring to the tokens list
                    substring = '' # Reset substring after appending
                    subtokens.append(char) # Appending to tokens symbol char indivually
            # Updating raw token index
            position += 1
        
        return subtokens


    def parse_hashtags_mentions(self, raw_token, hashtag=True):

        '''
        - Hashtags and mentions parser -
        
        Returns (un)parsed token plus:
         -1: invalid           e.g. #-hashtag (no parsing done)
          0: partially valid   e.g. #hash.tag
          1: fully valid       e.g. #hashtag
        '''

        # Initializing validity of raw token (as invalid)
        valid_hashtag_mention = -1

        # Initializing auxiliar variables
        subtokens, substring, index = [], '', 0

        # Processing each character excluding the first one
        for char in raw_token[1:]:

            # Checking for invalid characters
            if not re.match(self.invalid_hashtags_mentions_chars, char):
                substring += char # Building substring hashtag until invalid token is found
                index += 1

            # Character is invalid
            else:
                # Invalid hashtag or mention (contains invalid character right after '#' or '@')
                if index == 0:
                    return [], valid_hashtag_mention
                break
        
        # Updating truth value of valid_hashtag_mention 
        # Raw token as a whole is a valid hashtag or mention
        if substring and not raw_token[index+1:len(raw_token)]:
            valid_hashtag_mention = 1
        # Raw token contains a valid hashtag or mention but has an invalid right hand side
        else:
            valid_hashtag_mention = 0

        # Tokenizes valid hashtag / mention
        subtokens.append('#' + substring) if hashtag else subtokens.append('@' + substring)

        # Tokenizes rest of the (invalid) hashtag so it can be handled as any other split
        if raw_token[index+1:len(raw_token)]:
            subtokens.append(raw_token[index+1:len(raw_token)])
        
        return subtokens, valid_hashtag_mention


    # Exemplifies how Twikenizer handles different situations
    def examplify(self):

        tweet = 'Tw33t a_!aa&!a?b #%lol # @dude_really #hash_tag $hit (g@y) (retard#d) @dude. \U0001F600\U0001F600 !\U0001F600abc %\U0001F600lol #hateit #hate.it $%&/ f*ck-'

        print('Generated tweet\n---------------')
        print(tweet + '\n')
        
        tokens = self.tokenize(tweet)

        print('Generated tokens\n----------------')
        print(tokens)
