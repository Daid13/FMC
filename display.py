import jinja2

environment = jinja2.Environment(loader=jinja2.FileSystemLoader("templates/"))
display_template= environment.get_template("start.html")
context={"current_term": "in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out",
         "operation_result":"c<_>.[3].in<y>.[y]c.[y].+.<p>.[p]out"}
display_template.render(context)
