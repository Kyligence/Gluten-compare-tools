
def write_csv(file, *content):
    content_to_write = ",".join([str(x) for x in content]) + "\n"

    with open(file, "a+") as detail:
        detail.write(content_to_write)
