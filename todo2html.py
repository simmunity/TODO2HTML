# ToDo List converter from a Markup syntax to HTML and also converting from HTML back to Markup
# Written using PyCharm and Python 3.4 by Shannon Bailey Friday July 28, 2017 on a Macbook Pro

import sys

# define state machine constants
SECTION_START  = 0
SECTION_END    = 1
HEADLINE_START = 2
HEADLINE_END   = 3
LIST_START     = 4
LIST_END       = 5
ITEM_START     = 6
ITEM_END       = 7
HEADING        = 8
ITEM           = 9
DONE           = 10

# define matching html tags for state machine constants
tags = ['<section>', '</section>', '<h2>', '</h2>', '<ol>', '</ol>', '<il>', '</il>', '', '', '']


def read_file (file_name ):
    infile = open (file_name)
    temp = infile.read ()
    infile.close ()
    return temp


def write_file (file_name, output):
    outfile = open (file_name, 'w')
    outfile.write (output)
    outfile.close ()


# main routine checks the parameters and chooses how to convert the input file
def main ():
    print ('ToDo List to HTML converter and reversion tool, STB V0.1')

    if len(sys.argv) != 4:
        print ('Command arguments are: --toHtml markupFile htmlFile')
        print ('or: --fromHTML htmlFile markupFile')
        exit ()

    command          = sys.argv[1]
    input_file_name  = sys.argv[2]
    output_file_name = sys.argv[3]

    text = read_file (input_file_name)

    if command == '--toHtml':
        print ('Converting to HTML')
        output = mu_to_html (text)

    elif command == '--fromHtml':
        print ('Reverting HTML to Markup')
        output = html_to_mu (text)

    else:
        print ('Invalid conversion argument = ', command)
        exit ()

    write_file (output_file_name, output)

# disable the following 2 lines for normal operation
    mu_output = html_to_mu (output)        # for testing convert from markup to HTML and back to markup each time
    write_file ('markupGenerated', mu_output)


# decode the markup to do list and convert it to HTML
def mu_to_html (text):
    output_html   = ''
    state         = HEADING
    line          = 0

    split_text        = text.splitlines()
    split_text_length = len(split_text)

    while state != DONE:
        if line >= split_text_length - 1:
            state = DONE

        if state == HEADING:
            split_line = split_text[line].split ()
            split_line_length = len (split_line)

            if split_line_length <= 2:
                print ('Invalid header')
                exit ()

            if split_line[0] == '==':
                if '==' == split_line[split_line_length - 1]:
                    output_html += '<section>' + '\n' + '<h2>'
                    for index in range (1, split_line_length - 1):
                        output_html += split_line[index]
                        if index < split_line_length - 2:
                            output_html += ' '

                    output_html += '</h2>' + '\n'
                else:
                    print ('Invalid header, no matching == found')
                    exit ()
            else:
                print ('Invalid header, no initial == found')
                exit ()

            line += 1
            state = ITEM

            first_item = 1
            while state == ITEM:
                if line >= split_text_length:
                    if first_item != 1:
                        output_html += '</ol>\n</section>\n'
                    state = DONE
                else:
                    split_line = split_text[line].split()
                    split_line_length = len(split_line)

                    if split_line_length == 0:
                        line += 1

                    else:
                        if split_line[0] == '==':
                            if first_item != 1:
                                output_html += '</ol>\n</section>\n'
                                state = HEADING

                        else:
                            if split_line[0] == '*':
                                if first_item == 1:
                                    first_item = 0
                                    output_html += '<ol>'

                                output_html += '<li>'
                                for index in range (1, split_line_length):
                                    output_html += split_line[index]
                                    if index < split_line_length - 1:
                                        output_html += ' '

                                output_html += '</li>'
                                line += 1
                            else:
                                print ('Invalid item encountered = ', split_text[line])
                                exit ()
    return output_html


# seperate html tags from text while creating a list out of the tags and text sections
def tag_split (text):
    tokens = []
    start  = 0
    end    = 0
    length = len (text)
    while start < length:
        if text[start] == '\n':   # remove newlines
            start += 1
        else:
            end = start + 1
            if text[start] == '<':
                while end < length:
                    if text[end] == '>':
                        tokens.append (text[start:end + 1])
                        start = end + 1
                        end = length
                    end += 1
            else:
                while end < length:
                    if text[end] == '<':
                        tokens.append (text[start:end])
                        start = end
                        end = length
                    end += 1
    return tokens


# decode the HTML and verify it conforms to an expected sequence of nested tags
def html_to_mu (text):
    output_md  = ''
    state      = SECTION_START
    element    = 0

    split_text        = tag_split (text)
    split_text_length = len(split_text)

    while state != DONE:
        if element >= split_text_length - 1:
            state = DONE
            break

        tag_or_text = split_text[element]
        for index in range (0, HEADING):
            if tag_or_text == tags[index]:
                if state != index:
                    print ('Expected HTML tag ' + tags[state] + ' but encountered ' + tags[index])
                state = index
                break

        if state == SECTION_START:
            state = HEADLINE_START

        elif state == SECTION_END:
            state = SECTION_START

        elif state == HEADLINE_START:
            output_md += '== '
            state = HEADING

        elif state == HEADING:
            output_md += tag_or_text
            state = HEADLINE_END

        elif state == HEADLINE_END:
            output_md += ' ==\n'
            state = LIST_START

        elif state == LIST_START:
            state = ITEM_START

        elif state == LIST_END:
            state = SECTION_END

        elif state == ITEM_START:
            state = ITEM

        elif state == ITEM:
            output_md += '* ' + tag_or_text + '\n'
            state = ITEM_END

        elif state == ITEM_END:
            if element < split_text_length - 1:
                if split_text[element + 1] == tags[LIST_END]:
                    state = LIST_END
                else:
                    state = ITEM_START

        else:
            print ('Invalid HTML encountered, exiting')
            exit ()

        element += 1

    return output_md


# invoke the main program function
main ()
