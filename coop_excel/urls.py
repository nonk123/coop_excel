from django.urls import path
from django.shortcuts import render

from .lisp import functions

def documentation(req, query=""):
    show_help = not bool(query)

    if not query:
        query = ",".join(functions.keys())

    info = []

    for name in query.split(","):
        if name not in functions:
            info.append({
                "found": False,
                "name": name
            })
        else:
            fun = functions[name]

            args = []

            for i, param in enumerate(fun.lisp_args):
                if i == 0:
                    continue

                args.append(param)

                if param.startswith("*"):
                    args[-1] = args[-1][1:] + "..."

            info.append({
                "found": True,
                "name": name,
                "doc": fun.__doc__,
                "args": args
            })

    return render(req, "coop_excel/doc.html", {
        "functions": info,
        "show_help": show_help
    })

urlpatterns = [
    path("", lambda req: render(req, "coop_excel/index.html"), name="index"),
    path("doc/", documentation, name="doc"),
    path("doc/<query>/", documentation, name="doc")
]
