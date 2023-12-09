import json
import random
import string

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_log_line(template):
    line = []
    for part in template:
        if part == '<word>':
            line.append(generate_random_string(random.randint(min_word_length, max_word_length)))
        else:
            line.append(part)
    return ' '.join(line)

def generate_templates(num_templates, max_line_length, min_line_length):
    templates = []
    for _ in range(num_templates):
        template = []
        num_parts = random.randint(min_line_length, max_line_length)  # Random number of parts in the template
        for _ in range(num_parts):
            if random.random() < 0.3:  # 30% chance to add a word placeholder
                template.append('<word>')
            else:
                template.append(generate_random_string(random.randint(3, 8)))  # Random non-word part

        templates.append(template)
    return templates


with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    max_word_length = config['max_word_length']
    min_word_length = config['min_word_length']
    common_templates = config['common_templates']
    num_lines = config['num_lines']
    num_common_templates = config['num_random_common_templates']
    min_line_legth = config['min_line_length']
    max_line_length = config['max_line_length']
    diff_templates = config['diff_templates']
    num_diff_templates = config["num_random_diff_templates"]
    diff_template_chance = float(config["diff_template_chance_percent"]) / 100.0


random_templates = generate_templates(num_common_templates, max_line_length, min_line_legth)
common_templates.extend(random_templates)

random_diff_templates = generate_templates(num_diff_templates, max_line_length, min_line_legth)
diff_templates.extend(random_templates)

with open('./output/log1.txt', 'w') as file1, open('./output/log2.txt', 'w') as file2:
    for i, _ in enumerate(range(num_lines)):
        template_index = random.randint(0, len(common_templates) - 1)
        template1 = common_templates[template_index]
        template2 = common_templates[template_index].copy()
        timestamp = f"[{i}.0] "

        # Making a small difference in the second log by changing a part of the template
        if random.random() < diff_template_chance:
            diff_template_index = random.randint(0, len(diff_templates) - 1)
            template2 = diff_templates[diff_template_index]

        log_line1 = timestamp + generate_log_line(template1)
        log_line2 = timestamp + generate_log_line(template2)

        file1.write(log_line1 + '\n')
        file2.write(log_line2 + '\n')
