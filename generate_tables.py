import argparse
import json


def remove_domains(data_dict, kw_dict, to_remove):
    for domain in to_remove:
        if domain in data_dict:
            del data_dict[domain]

    for domain in to_remove:
        if domain in kw_dict:
            del kw_dict[domain]


def calculate_ranks(data_dict, kw_dict):
    ranks = {}

    for url in data_dict.keys():
        if data_dict[url]['count'] >= 5:
            start = 0
            mid = 0
            end = 0
            total = 0
            for num in data_dict[url]['page_nums']:
                if num <= 0.3:
                    start += 1
                elif num < 0.75:
                    mid += 1
                elif num >= 0.75:
                    end += 1
                total += 1
            ranks[url] = (start, mid, end, total)

    for keyword in kw_dict.keys():
        if kw_dict[keyword]['count'] >= 5:
            start = 0
            mid = 0
            end = 0
            total = 0

            for num in kw_dict[keyword]['page_nums']:
                if num <= 0.3:
                    start += 1
                elif num < 0.75:
                    mid += 1
                elif num >= 0.75:
                    end += 1
                total += 1

            if keyword not in ranks.keys():
                ranks[keyword] = (start, mid, end, total)
            else:
                if total > ranks[keyword][3]:
                    ranks[keyword] = (start, mid, end, total)

    return ranks


def print_results(ranks, output_file):
    with open(output_file, 'w') as f:
        for key, value in ranks.items():
            f.write(f"{key} {value}\n")


def main(urls_file, keywords_file, to_remove_file, output_file):
    with open(urls_file) as json_f:
        data_dict = json.load(json_f)

    with open(keywords_file) as json_f:
        kw_dict = json.load(json_f)

    with open(to_remove_file, encoding='utf-8') as file:
        to_remove = [line.strip() for line in file]

    remove_domains(data_dict, kw_dict, to_remove)
    ranks = calculate_ranks(data_dict, kw_dict)

    with open(output_file + '.txt', 'w') as output:
        output.write("Rank\tItem\tCount\n")
        output.write("----------------------\n")
        for index, (item, count) in enumerate(ranks.items(), start=1):
            output.write("{:<5}\t{:<50}\t{}\n".format(index, item, count))

    ranks = dict(sorted(ranks.items(), key=lambda item: -item[1][0]))
    print_results(ranks, output_file + "_introduction.txt")

    ranks = dict(sorted(ranks.items(), key=lambda item: -item[1][1]))
    print_results(ranks, output_file + "_research.txt")

    ranks = dict(sorted(ranks.items(), key=lambda item: -item[1][2]))
    print_results(ranks, output_file + "_discussion_conclusion.txt")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process URLs and keywords.')
    parser.add_argument('urls_file', type=str, help='Path to the URLs JSON file')
    parser.add_argument('keywords_file', type=str, help='Path to the keywords JSON file')
    parser.add_argument('to_remove_file', type=str, help='Path to the to_remove text file')
    parser.add_argument('output_file', type=str, help='Path to the output file prefix')
    args = parser.parse_args()

    main(args.urls_file, args.keywords_file, args.to_remove_file, args.output_file)
