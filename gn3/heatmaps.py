"""
This module will contain functions to be used in computation of the data used to
generate various kinds of heatmaps.
"""

from functools import reduce
from typing import Any, Dict, Sequence
from gn3.computations.slink import slink
from gn3.computations.qtlreaper import generate_traits_file
from gn3.computations.correlations2 import compute_correlation
from gn3.db.genotypes import build_genotype_file, load_genotype_samples
from gn3.db.traits import (
    retrieve_trait_data,
    retrieve_trait_info,
    generate_traits_filename)

def export_trait_data(
        trait_data: dict, strainlist: Sequence[str], dtype: str = "val",
        var_exists: bool = False, n_exists: bool = False):
    """
    Export data according to `strainlist`. Mostly used in calculating
    correlations.

    DESCRIPTION:
    Migrated from
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/base/webqtlTrait.py#L166-L211

    PARAMETERS
    trait: (dict)
      The dictionary of key-value pairs representing a trait
    strainlist: (list)
      A list of strain names
    dtype: (str)
      ... verify what this is ...
    var_exists: (bool)
      A flag indicating existence of variance
    n_exists: (bool)
      A flag indicating existence of ndata
    """
    def __export_all_types(tdata, strain):
        sample_data = []
        if tdata[strain]["value"]:
            sample_data.append(tdata[strain]["value"])
            if var_exists:
                if tdata[strain]["variance"]:
                    sample_data.append(tdata[strain]["variance"])
                else:
                    sample_data.append(None)
            if n_exists:
                if tdata[strain]["ndata"]:
                    sample_data.append(tdata[strain]["ndata"])
                else:
                    sample_data.append(None)
        else:
            if var_exists and n_exists:
                sample_data += [None, None, None]
            elif var_exists or n_exists:
                sample_data += [None, None]
            else:
                sample_data.append(None)

        return tuple(sample_data)

    def __exporter(accumulator, strain):
        # pylint: disable=[R0911]
        if strain in trait_data["data"]:
            if dtype == "val":
                return accumulator + (trait_data["data"][strain]["value"], )
            if dtype == "var":
                return accumulator + (trait_data["data"][strain]["variance"], )
            if dtype == "N":
                return accumulator + (trait_data["data"][strain]["ndata"], )
            if dtype == "all":
                return accumulator + __export_all_types(trait_data["data"], strain)
            raise KeyError("Type `%s` is incorrect" % dtype)
        if var_exists and n_exists:
            return accumulator + (None, None, None)
        if var_exists or n_exists:
            return accumulator + (None, None)
        return accumulator + (None,)

    return reduce(__exporter, strainlist, tuple())

def trait_display_name(trait: Dict):
    """
    Given a trait, return a name to use to display the trait on a heatmap.

    DESCRIPTION
    Migrated from
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/base/webqtlTrait.py#L141-L157
    """
    if trait.get("db", None) and trait.get("trait_name", None):
        if trait["db"]["dataset_type"] == "Temp":
            desc = trait["description"]
            if desc.find("PCA") >= 0:
                return "%s::%s" % (
                    trait["db"]["displayname"],
                    desc[desc.rindex(':')+1:].strip())
            return "%s::%s" % (
                trait["db"]["displayname"],
                desc[:desc.index('entered')].strip())
        prefix = "%s::%s" % (
            trait["db"]["dataset_name"], trait["trait_name"])
        if trait["cellid"]:
            return "%s::%s" % (prefix, trait["cellid"])
        return prefix
    return trait["description"]

def cluster_traits(traits_data_list: Sequence[Dict]):
    """
    Clusters the trait values.

    DESCRIPTION
    Attempts to replicate the clustering of the traits, as done at
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/Heatmap.py#L138-L162
    """
    def __compute_corr(tdata_i, tdata_j):
        if tdata_i[0] == tdata_j[0]:
            return 0.0
        corr_vals = compute_correlation(tdata_i[1], tdata_j[1])
        corr = corr_vals[0]
        if (1 - corr) < 0:
            return 0.0
        return 1 - corr

    def __cluster(tdata_i):
        return tuple(
            __compute_corr(tdata_i, tdata_j)
            for tdata_j in enumerate(traits_data_list))

    return tuple(__cluster(tdata_i) for tdata_i in enumerate(traits_data_list))

def heatmap_data(traits_names, conn: Any):
    """
    heatmap function

    DESCRIPTION
    This function is an attempt to reproduce the initialisation at
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/Heatmap.py#L46-L64
    and also the clustering and slink computations at
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/Heatmap.py#L138-L165
    with the help of the `gn3.computations.heatmap.cluster_traits` function.

    It does not try to actually draw the heatmap image.

    PARAMETERS:
    TODO: Elaborate on the parameters here...
    """
    threshold = 0 # webqtlConfig.PUBLICTHRESH
    def __retrieve_traitlist_and_datalist(threshold, fullname):
        trait = retrieve_trait_info(threshold, fullname, conn)
        return (trait, retrieve_trait_data(trait, conn))

    traits_details = [
        __retrieve_traitlist_and_datalist(threshold, fullname)
        for fullname in traits_names]
    traits_list = tuple(x[0] for x in traits_details)
    traits_data_list = [x[1] for x in traits_details]
    genotype_filename = build_genotype_file(traits_list[0]["riset"])
    strainlist = load_genotype_samples(genotype_filename)
    exported_traits_data_list = tuple(
        export_trait_data(td, strainlist) for td in traits_data_list)
    slink_data = slink(cluster_traits(exported_traits_data_list))
    ordering_data = compute_heatmap_order(slink_data)
    strains_and_values = retrieve_strains_and_values(
        ordering_data, strainlist, exported_traits_data_list)
    strains_values = strains_and_values[0][1]
    trait_values = [t[2] for t in strains_and_values]
    traits_filename = generate_traits_filename()
    generate_traits_file(strains_values, trait_values, traits_filename)

    return {
        "slink_data": slink_data,
        "ordering_data": ordering_data,
        "strainlist": strainlist,
        "genotype_filename": genotype_filename,
        "traits_list": traits_list,
        "traits_data_list": traits_data_list,
        "exported_traits_data_list": exported_traits_data_list,
        "traits_filename": traits_filename
    }

def compute_traits_order(slink_data, neworder: tuple = tuple()):
    """
    Compute the order of the traits for clustering from `slink_data`.

    This function tries to reproduce the creation and update of the `neworder`
    variable in
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/Heatmap.py#L120
    and in the `web.webqtl.heatmap.Heatmap.draw` function in GN1
    """
    def __order_maker(norder, slnk_dt):
        if isinstance(slnk_dt[0], int) and isinstance(slnk_dt[1], int):
            return norder + (slnk_dt[0], slnk_dt[1])

        if isinstance(slnk_dt[0], int):
            return __order_maker((norder + (slnk_dt[0], )), slnk_dt[1])

        if isinstance(slnk_dt[1], int):
            return __order_maker(norder, slnk_dt[0]) + (slnk_dt[1], )

        return __order_maker(__order_maker(norder, slnk_dt[0]), slnk_dt[1])

    return __order_maker(neworder, slink_data)

def retrieve_strains_and_values(orders, strainlist, traits_data_list):
    """
    Get the strains and their corresponding values from `strainlist` and
    `traits_data_list`.

    This migrates the code in
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/Heatmap.py#L215-221
    """
    # This feels nasty! There's a lot of mutation of values here, that might
    # indicate something untoward in the design of this function and its
    # dependents  ==>  Review
    strains = []
    values = []
    rets = []
    for order in orders:
        temp_val = traits_data_list[order]
        for i, strain in enumerate(strainlist):
            if temp_val[i] is not None:
                strains.append(strain)
                values.append(temp_val[i])
        rets.append([order, strains[:], values[:]])
        strains = []
        values = []

    return rets

def nearest_marker_finder(genotype):
    """
    Returns a function to be used with `genotype` to compute the nearest marker
    to the trait passed to the returned function.

    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/Heatmap.py#L425-434
    """
    def __compute_distances(chromo, trait):
        loci = chromo.get("loci", None)
        if not loci:
            return None
        return tuple(
            {
                "name": locus["name"],
                "distance": abs(locus["Mb"] - trait["mb"])
            } for locus in loci)

    def __finder(trait):
        _chrs = tuple(
            _chr for _chr in genotype["chromosomes"]
            if str(_chr["name"]) == str(trait["chr"]))
        if len(_chrs) == 0:
            return None
        distances = tuple(
            distance for dists in
            filter(
                lambda x: x is not None,
                (__compute_distances(_chr, trait) for _chr in _chrs))
            for distance in dists)
        nearest = min(distances, key=lambda d: d["distance"])
        return nearest["name"]
    return __finder

def get_nearest_marker(traits_list, genotype):
    """
    Retrieves the nearest marker for each of the traits in the list.

    DESCRIPTION:
    This migrates the code in
    https://github.com/genenetwork/genenetwork1/blob/master/web/webqtl/heatmap/Heatmap.py#L419-L438
    """
    if not genotype["Mbmap"]:
        return [None] * len(trait_list)

    marker_finder = nearest_marker_finder(genotype)
    return [marker_finder(trait) for trait in traits_list]

def get_lrs_from_chr(trait, chr_name):
    chromosome = trait["chromosomes"].get(chr_name)
    if chromosome:
        return [
            locus["LRS"] for locus in
            sorted(chromosome["loci"], key=lambda loc: loc["Locus"])]
    return [None]

# # Grey + Blue + Red
# def generate_heatmap():
#     cols = 20
#     y_axis = (["%s"%x for x in range(1, cols+1)][:-1] + ["X"]) #replace last item with x for now
#     x_axis = heatmap_x_axis_names()
#     data = generate_random_data(height=cols, width=len(x_axis))
#     fig = px.imshow(
#         data,
#         x=x_axis,
#         y=y_axis,
#         width=500)
#     fig.update_traces(xtype="array")
#     fig.update_traces(ytype="array")
#     # fig.update_traces(xgap=10)
#     fig.update_xaxes(
#         visible=True,
#         title_text="Traits",
#         title_font_size=16)
#     fig.update_layout(
#         coloraxis_colorscale=[
#             [0.0, '#3B3B3B'], [0.4999999999999999, '#ABABAB'],
#             [0.5, '#F5DE11'], [1.0, '#FF0D00']])
#     fig.write_html("%s/%s"%(heatmap_dir, "test_image.html"))
#     return fig
