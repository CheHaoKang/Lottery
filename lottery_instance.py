from BingoBingo import BingoBingo

if __name__ == "__main__":
    bingo_bingo = BingoBingo()

    bingo_bingo.crawler()

    sorted_number_occurrence = bingo_bingo.number_statistics()
    email_content = ''
    for pair in sorted_number_occurrence:
        email_content += pair[0] + ': ' + str(pair[1]) + "\n"

    bingo_bingo.send_email(email_content)
    