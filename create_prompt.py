import jinja2
import os

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Read the contents of each file
template_content = read_file('prompt.tmpl')
post_structure_content = read_file('post_structure.txt')
example_post_content = read_file('_posts/2023-06-15-chrome-extension-first-development.html')

# Create a Jinja2 environment and template
env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
template = env.from_string(template_content)

# Render the template with the file contents
rendered_content = template.render(
    post_structure_content=post_structure_content,
    example_post_content=example_post_content
)

# Write the rendered content to a new file
output_file = 'combined_prompt.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(rendered_content)

print(f"Combined content written to {output_file}")
