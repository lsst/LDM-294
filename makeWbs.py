import csv
import glob
import os
import sys
from collections import OrderedDict


def get_products_for_wbs(productlist, wbs, wbs_list):
    # Return a list of product descriptions which match the specified WBS
    # element.
    # We return products at the finest level of WBS to which they correspond.
    # That is, if a product is listed in, say, "1.02C.05.03.04", and we have a
    # WBS description for that element exactly, we return it there. If we
    # don't have that element but do have "1.02C.05.03", we return it there.
    products = []

    def score(target, candidate):
        # Quality of match of candidate WBS to target.
        # Low scores are better matches.
        partitioned = target.partition(candidate)
        return 10 * len(partitioned[0]) + len(partitioned[2])

    with open(productlist, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row["WBS"].startswith("1"):
                # If this doesn't look like a construction WBS, ignore it.
                # Note that only leaf products have a WBS defined: this is
                # intentional.
                continue

            def score_key(cand):
                return score(row["WBS"], cand)
            if min(wbs_list, key=score_key) == wbs:
                products.append(row["Description"])

    return products


def get_wbs_descriptions(wbsdir):
    # Return an OrderedDict of WBS element to LaTeX-formatted description.

    def filename_to_wbs(wbs):
        # Drop the directory name and the ".tex" suffix.
        return os.path.basename(wbs)[:-4]

    def wbs_key(wbs):
        # Return a key suitable for sorting WBS elements.
        vals = [x.strip('C') for x in filename_to_wbs(wbs).split(".")]
        total = 0
        multiplier = 100.0
        for val in vals:
            # Increment by one to avoid 02C.04 and 02C.04.00 sorting as
            # equivalent
            total += (float(val) + 1.0) * multiplier
            multiplier /= 100
        return total

    texfiles = sorted(glob.glob(os.path.join(wbsdir, "*.tex")), key=wbs_key)
    wbs_descriptions = OrderedDict()
    for texfile in texfiles:
        with open(texfile, "r") as f:
            wbs_descriptions[filename_to_wbs(texfile)] = f.read()

    return wbs_descriptions


def format_products(products):
    # Return a LaTeX-formatted itemization of the products listed.
    if not products:
        output = "\nNo products are defined at this level of the WBS.\n\n"

    else:
        output = "\nThe following products (per \secref{sect:products}) are defined at this level of WBS:\n\n"
        output += "\\begin{itemize}\n"
        for product in products:
            output += "\\item{%s}\n" % (product,)
        output += "\end{itemize}\n\n"

    return output


if __name__ == "__main__":
    try:
        productlist = sys.argv[1]
    except IndexError:
        productlist = "DM Product Properties.csv"

    try:
        wbsdir = sys.argv[2]
    except IndexError:
        wbsdir = "wbs"

    try:
        output = sys.argv[3]
    except IndexError:
        output = "wbslist.tex"

    with open(output, "w") as out:
        out.write("% THIS FILE IS AUTOMATICALLY GENERATED: DO NOT EDIT\n\n")
        wbs_descriptions = get_wbs_descriptions(wbsdir)
        wbs_list = wbs_descriptions.keys()
        for wbs, desc in wbs_descriptions.items():
            out.write(desc)
            out.write(format_products(get_products_for_wbs(productlist,
                      wbs, wbs_list)))
