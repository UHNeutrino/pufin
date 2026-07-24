# file: WeightMain.py

from __future__ import annotations

import argparse
import array
import json5
import os
import re
from pathlib import Path

import ROOT

import GlobalV
import ParticlePlots as pp
import SetupFunctions as sf


HOME = os.getenv("HOME", "/home/lboe")
BASE_OUT = "/data/t2k-nova"

#### Define filename pattern expected for PUfIN ROOT files #####
FILENAME_RE = re.compile(
    r"^Flat_"
    r"(?P<generator_version>[^_]+)_"
    r"(?P<tune>[^_]+)_"
    r"(?P<interaction>CC|NC)_"
    r"(?P<flavor>NuMu|NuMuBar|NuE|NuEBar)_"
    r"(?P<energy_range>\d+-\d+GeV)_"
    r"(?P<target>[A-Za-z0-9]+)_"
    r"(?P<events>[^.]+)\.root$"
)

### Creates a dictionary relating target names (like Carbon) to a label (C12) -> EX: "Carbon": "C12" ####
TARGET_DIR_TO_LABEL = {
    v["name"]: v["label"] for v in GlobalV.NovaTargets.values()
}


def load_json5(path: str | Path) -> dict:
    with open(path, "r") as f:
        return json5.load(f)

#### Clean up lists: remove blank entries and strip blank spaces ####
def normalize_list(values):
    if values is None:
        return None
    if isinstance(values, str):
        return [values]
    values = [str(v).strip() for v in values if str(v).strip()]
    return values if values else None

#### Take a ROOT filename/path and turn it into a metadata dictionary ####
def parse_pufin_filename(path: str | Path) -> dict: # input can be string path or Path object
    path = Path(path) # converts into a Path object so you can use path.name and path.parent.name 
    match = FILENAME_RE.match(path.name)  # checks the name of the file to see if it matches the filename pattern
    if not match:
        raise ValueError(f"Unrecognized PUfIN filename: {path.name}")

    meta = match.groupdict() # Turns all the pieces of the filename into a dictionary
    meta["path"] = str(path)
    meta["target_dir"] = path.parent.name # Ex: Carbon
    meta["target_from_dir"] = TARGET_DIR_TO_LABEL.get(path.parent.name, path.parent.name) # Ex: Carbon -> C12
    return meta


#### Looks through generator/target directories, checks that they exist, gets metadata from filenames and returns list of discovered files ####
def discover_pufin_files(base_dir: str, generator: str) -> list[dict]:
    generator_dir = Path(base_dir) / generator.upper()
    if not generator_dir.is_dir():
        raise FileNotFoundError(f"Missing generator directory: {generator_dir}")

    discovered = []
    for target_dir in sorted(generator_dir.iterdir()):
        if not target_dir.is_dir():
            continue

        for root_file in sorted(target_dir.glob("Flat_*.root")):
            meta = parse_pufin_filename(root_file)
            discovered.append(meta)

    return discovered

#### Gets filters from either command line arguments or config file and returns a dictionary ####
def get_filters(config_stage2: dict, args) -> dict:
    config_filters = config_stage2.get("filters", {})

    interactions = normalize_list(args.interaction) or normalize_list(config_filters.get("interactions"))
    flavors = normalize_list(args.flavor) or normalize_list(config_filters.get("flavors"))
    energy_ranges = normalize_list(args.energy_range) or normalize_list(config_filters.get("energy_ranges"))
    targets = normalize_list(args.target) or normalize_list(config_filters.get("targets"))

    return {
        "interactions": interactions,
        "flavors": flavors,
        "energy_ranges": energy_ranges,
        "targets": targets,
    }

#### Groups files together based on requested filters ####
def group_by_sample_and_target(file_meta: list[dict]) -> list[dict]:
    grouped = {}
    for meta in file_meta:
        key = (
            meta["interaction"],
            meta["requested_flavor"],
            meta["energy_range"],
            meta["target"],
        )
        grouped.setdefault(key, []).append(meta)

    out = []
    for key in sorted(grouped):
        interaction, requested_flavor, energy_range, target = key
        out.append(
            {
                "interaction": interaction,
                "requested_flavor": requested_flavor,
                "energy_range": energy_range,
                "target": target,
                "files": grouped[key],
            }
        )
    return out

# def expand_requested_nc_flavors(flavors):
#     if not flavors:
#         return None
#     return list(flavors)

#### If requested_flavor = NC NuE(NuEBar), the code uses NC NuMu(NuMuBar) ROOT files and xsec splines since they are the same ####
def resolve_source_flavor(interaction: str, requested_flavor: str):
    if interaction != "NC":
        return requested_flavor

    if requested_flavor == "NuMu":
        return "NuMu"
    if requested_flavor == "NuE":
        return "NuMu"
    if requested_flavor == "NuMuBar":
        return "NuMuBar"
    if requested_flavor == "NuEBar":
        return "NuMuBar"

    raise ValueError(f"Unsupported requested flavor '{requested_flavor}'")

#### Takes discovered files, applies filters, handles NC flavor mapping, and returns final metadata ####
def build_selected_entries(discovered: list[dict], filters: dict) -> list[dict]:
    requested_flavors = filters["flavors"] or ["NuMu", "NuMuBar", "NuE", "NuEBar"]

    selected = []
    for meta in discovered:
        if filters["interactions"] and meta["interaction"] not in filters["interactions"]:
            continue
        if filters["energy_ranges"] and meta["energy_range"] not in filters["energy_ranges"]:
            continue
        if filters["targets"] and meta["target"] not in filters["targets"]:
            continue

        for requested_flavor in requested_flavors:
            source_flavor = resolve_source_flavor(meta["interaction"], requested_flavor) # Identifies the correct file to use for NC Nue(NuEBar)
            xsec_flavor = source_flavor # Always use the xsec spline that matches the flavor used to generate the file

            if meta["flavor"] != source_flavor:
                continue

            selected_meta = dict(meta)
            selected_meta["requested_flavor"] = requested_flavor
            selected_meta["source_flavor"] = source_flavor
            selected_meta["xsec_flavor"] = xsec_flavor
            selected.append(selected_meta)

    return selected

def print_discovery_summary(grouped: list[dict]) -> None:
    print("\n========== DISCOVERY SUMMARY ==========")
    for group in grouped:
        target = group["target"]
        files = group["files"]
        print(f"\nTarget {target}: {len(files)} file(s)")

        by_sample = {}
        for meta in files:
            key = (meta["interaction"], meta["flavor"], meta["energy_range"])
            by_sample[key] = by_sample.get(key, 0) + 1

        for interaction, flavor, energy_range in sorted(by_sample):
            print(f"  {interaction:>2} {flavor:>7} {energy_range:>8}: {by_sample[(interaction, flavor, energy_range)]}")
    print("=======================================\n")


def apply_global_definitions(df, global_settings):
    if global_settings.get("EvisB", False):
        df = pp.DefineEvis(df)
    if global_settings.get("KinematicsB", False):
        df = pp.DefineKinematics(df)
    if global_settings.get("TkiB", False):
        df = pp.DefineTKI(df)
    if global_settings.get("ThresholdsB", False):
        df = pp.FlagParticleThresholds(df)
    return df


def build_hist_model(same1d: dict):
    bins = same1d["Bins"]
    use_vbins = same1d["VBins"][0]

    if use_vbins:
        vbins = array.array("d", same1d["VBins"][1])
        return ROOT.RDF.TH1DModel(
            "h_weighted_total",
            "h_weighted_total",
            len(vbins) - 1,
            vbins,
        )

    return ROOT.RDF.TH1DModel(
        "h_weighted_total",
        "h_weighted_total",
        bins[0],
        bins[1],
        bins[2],
    )


def parse_axis_info(same1d: dict):
    axis_info = [x.strip() for x in same1d["AxisInfo"].split(",")]
    if len(axis_info) != 5:
        raise ValueError("same1D['AxisInfo'] must have 5 comma-separated fields")
    return axis_info


def format_total_hist(total_hist, same1d: dict):
    axis_info = parse_axis_info(same1d)
    xvar, xunit, yvar, yunit, plot_title = axis_info

    total_hist = sf.formatHist(
        total_hist,
        xvar,
        xunit,
        yvar,
        yunit,
        max=same1d.get("max", -1),
        PlotTitle=plot_title,
    )
    total_hist.SetDirectory(0)
    return total_hist, axis_info


def save_outputs(total_hist, component_hists, same1d, global_settings):
    save_dir = os.path.join(BASE_OUT, global_settings["Save"])
    os.makedirs(save_dir, exist_ok=True)

    base_name = same1d["Name"]
    total_hist, axis_info = format_total_hist(total_hist, same1d)

    root_path = os.path.join(save_dir, f"{base_name}.root")
    fout = ROOT.TFile(root_path, "RECREATE")

    for key, hist in component_hists.items():
        h_out = hist.Clone(f"h_{key}")
        h_out.SetDirectory(0)
        h_out.Write()

    h_total = total_hist.Clone("h_total")
    h_total.SetDirectory(0)
    h_total.Write()
    fout.Close()

    print(f"Saved {root_path}")

    img_ext = same1d.get("Ext", "png")
    pp.HOME = BASE_OUT
    pp.Savehist(
        total_hist,
        axis_info,
        global_settings["Save"],
        base_name,
        img_ext,
        max=same1d.get("max", -1),
        Normalize=same1d.get("Norm", False),
        logz=False,
    )

    img_path = os.path.join(save_dir, f"{base_name}.{img_ext}")
    print(f"Saved {img_path}")
    return total_hist


def make_fullmc_weighted_same1d(stage2: dict, global_settings: dict, args):
    discovered = discover_pufin_files(
        base_dir=args.base_dir or stage2["base_dir"],
        generator=args.generator or stage2["generator"],
    )

    filters = get_filters(stage2, args)
    selected = build_selected_entries(discovered, filters)
    grouped = group_by_sample_and_target(selected)

    if not grouped:
        raise RuntimeError("No PUfIN files matched the requested selection")

    print_discovery_summary(grouped)

    targets_file = os.path.expandvars(stage2["targets_file"])
    targets_cfg = load_json5(targets_file)
    
    
    target_weight_factors = targets_cfg.get("target_weight_factors", {})
    if not target_weight_factors:
        raise ValueError("targets file is missing 'target_weight_factors'")

    same1d = stage2["same1D"]
    reweight_cfg = stage2["reWeight"]

    hist_model = build_hist_model(same1d)
    total_hist = None
    component_hists = {}

    cut_expr = same1d.get("Cut", "")
    var_name = same1d["Var"]

    reweight_flag = reweight_cfg.get("enabled", False)
    # rw_file = reweight_cfg.get("rw_file", "")
    # rw_flux = reweight_cfg.get("rw_flux", "")
    xspline_mode = reweight_cfg["xspline_mode"]
    xsec_file = reweight_cfg["xsec_file"]
    xsec_mode_cfg = reweight_cfg["xsec_mode"]
    areaB = reweight_cfg.get("areaB", False)
    undoNormB = reweight_cfg.get("undoNormB", False)

    detector = args.detector or stage2["detector"]
    generator = args.generator or stage2["generator"]

    print("\n========== WEIGHTING ==========")

    for group in grouped:
        interaction = group["interaction"]
        requested_flavor = group["requested_flavor"]
        energy_range = group["energy_range"]
        target = group["target"]
        hist_key = f"{interaction}_{requested_flavor}_{target}"

        if target not in target_weight_factors:
            raise ValueError(f"Missing target weight factor for '{target}'")

        target_weight_factor = float(target_weight_factors[target])
        # print(f"\nTarget {target}")
        # print(f"  target_weight_factor = {target_weight_factor:.18e}")

        # target_hist = None
        # === TCHAIN CHANGE ===
        # These values are shared by every file in this group.
        
        first_meta = group["files"][0]
        source_flavor = first_meta["source_flavor"]
        xsec_flavor = first_meta["xsec_flavor"]
        flux_cfg = reweight_cfg["flux_inputs"][requested_flavor]
        rw_file = flux_cfg["rw_file"]
        rw_flux = flux_cfg["rw_flux"]
        energy_min, energy_max = parse_energy_range_window(energy_range)
        
        print(f"\nTarget {target}")
        print(f"  target_weight_factor = {target_weight_factor:.18e}")
        print(f"    sample = {interaction} {requested_flavor} {energy_range}")
        print(f"    source_flavor  = {source_flavor}")
        print(f"    requested_flavor = {requested_flavor}")
        print(f"    xsec_flavor    = {xsec_flavor}")
        print(f"    rw_file        = {rw_file}")
        print(f"    rw_flux        = {rw_flux}")
        print(f"    energy window  = [{energy_min}, {energy_max}] GeV")
        
        chain = ROOT.TChain("FlatTree_VARS")

        for meta in group["files"]:
            file_path = meta["path"]
            added = chain.Add(file_path)
            if added == 0:
                raise RuntimeError(f"Failed to add file to TChain: {file_path}")
            print(f"  added file           = {file_path}")
        chain_entries = chain.GetEntries()
        print(f"  chain files          = {chain.GetNtrees()}")
        print(f"  chain entries        = {chain_entries}")
        if chain.GetNtrees() == 0 or chain_entries == 0:
            raise RuntimeError(f"Empty TChain for {interaction} {requested_flavor} {energy_range} {target}")
            # interaction = meta["interaction"]
            # source_flavor = meta["source_flavor"]
            # requested_flavor = meta["requested_flavor"]
            # flux_cfg = reweight_cfg["flux_inputs"][requested_flavor]
            # rw_file = flux_cfg["rw_file"]
            # rw_flux = flux_cfg["rw_flux"]
            # xsec_flavor = meta["xsec_flavor"]
            # energy_range = meta["energy_range"]
            # energy_min, energy_max = parse_energy_range_window(energy_range)
            # print(f"    energy window   = [{energy_min}, {energy_max}] GeV")

            # print(f"  file: {file_path}")
            # print(f"    sample = {interaction} {requested_flavor} {energy_range}")
            # print(f"    source_flavor  = {source_flavor}")
            # print(f"    requested_flavor = {requested_flavor}")
            # print(f"    xsec_flavor    = {xsec_flavor}")
            # print(f"    rw_file        = {rw_file}")
            # print(f"    rw_flux        = {rw_flux}")
            # print(f"    energy window  = [{energy_min}, {energy_max}] GeV")

        # df = pp.CreateDataFrame(file_path, cut="None")
        df = pp.CreateDataFrame(chain, cut="None")
        df = apply_global_definitions(df, global_settings)

        weight_col = ""
        scale_factor = 1.0

        if reweight_flag:
            nu_type = GlobalV.FlavorToNuType[xsec_flavor]
            
            if xsec_mode_cfg == "auto":
                effective_xsec_mode = interaction
            else:
                effective_xsec_mode = xsec_mode_cfg

            spec = pp.get_target_reweight_spec(
                generator=generator,
                target=target,
                interaction=interaction,
                nu_type=nu_type,
                detector=detector,
                xsec_mode=effective_xsec_mode,
                xspline_mode=xspline_mode,
                xsec_file=xsec_file,
            )

            print(f"    effective_xsec_mode = {effective_xsec_mode}")
            
            df, bin_integral_unnorm = pp.defineWeightsSplineStage2(
                df,
                rw_file,
                rw_flux,
                spec,
                label=f"{generator}_{target}_{interaction}_{requested_flavor}_{energy_range}",
                Fscale=target_weight_factor,
                areaB=areaB,
                undoNormB=undoNormB,
                energy_min=energy_min,
                energy_max=energy_max,
            )
            weight_col = "weights"

            current = df.Sum(weight_col).GetValue()
            print(f"    current df.Sum(weights) = {current}")
            print(f"    target bin_integral_unnorm = {bin_integral_unnorm}")

            if current <= 0:
                raise RuntimeError(
                    f"Current weighted sum is non-positive for {interaction} {requested_flavor} {energy_range} {target}")

            scale_factor = bin_integral_unnorm / current
            print(f"    scale factor s = {scale_factor}")

        if cut_expr and cut_expr != "1":
            df_cut = df.Filter(cut_expr)
        else:
            df_cut = df

        if weight_col:
            rdf_hist = df_cut.Histo1D(hist_model, var_name, weight_col)
        else:
            rdf_hist = df_cut.Histo1D(hist_model, var_name)

        # hist = rdf_hist.GetValue().Clone()
        # hist.SetDirectory(0)

        # raw_integral = hist.Integral()
        
        target_hist = rdf_hist.GetValue().Clone(f"h_{hist_key}_{energy_range}")
        target_hist.SetDirectory(0)

        raw_integral = target_hist.Integral()
        if reweight_flag:
            print(f"    cut weighted histogram integral before s = {raw_integral}")
            # hist.Scale(scale_factor)
            target_hist.Scale(scale_factor)
            print(f"    cut weighted histogram integral after s = {target_hist.Integral()}")
        else:
            print(f"    raw histogram integral = {raw_integral}")

    #     if target_hist is None:
    #         target_hist = hist.Clone(f"h_{hist_key}")
    #         target_hist.SetDirectory(0)
    #     else:
    #         target_hist.Add(hist)

    #     print(f"    running target integral ({target}) = {target_hist.Integral()}")

    # if target_hist is None:
    #     continue
    
        if hist_key not in component_hists:
            component_hists[hist_key] = target_hist.Clone(f"h_{hist_key}")
            component_hists[hist_key].SetDirectory(0)
        else:
            component_hists[hist_key].Add(target_hist)

        print(f"  running component integral for {hist_key} = {component_hists[hist_key].Integral()}")

        if total_hist is None:
            total_hist = target_hist.Clone("h_weighted_total_combined")
            total_hist.SetDirectory(0)
        else:
            total_hist.Add(target_hist)

        print(f"  running total integral = {total_hist.Integral()}")

    if total_hist is None:
        raise RuntimeError("No histograms were created")

    print("\n========== FINAL SUMMARY ==========")
    # for target in sorted(component_hists):
    #     print(f"  {target}: {component_hists[target].Integral()}")
    for hist_key in sorted(component_hists):
        print(f"  {hist_key}: {component_hists[hist_key].Integral()}")
    print(f"  TOTAL: {total_hist.Integral()}")
    print("===================================\n")

    total_hist = save_outputs(total_hist, component_hists, same1d, global_settings)
    return total_hist


def parse_args():
    parser = argparse.ArgumentParser(description="PUfIN stage-2 weighting driver")

    parser.add_argument("--config", default="WeightMain.json5")
    parser.add_argument("--base-dir", default=None)
    parser.add_argument("--generator", default=None)
    parser.add_argument("--detector", default=None)

    parser.add_argument("--interaction", nargs="+", default=None)
    parser.add_argument("--flavor", nargs="+", default=None)
    parser.add_argument("--energy-range", nargs="+", default=None)
    parser.add_argument("--target", nargs="+", default=None)

    return parser.parse_args()

def parse_energy_range_window(energy_range: str):
    token = energy_range.replace("GeV", "")
    low_str, high_str = token.split("-")
    return float(low_str), float(high_str)


def main():
    args = parse_args()
    sf.setupRoot()

    config = load_json5(args.config)
    global_settings = config["global"]
    stage2 = config["stage2"]

    make_fullmc_weighted_same1d(stage2, global_settings, args)


if __name__ == "__main__":
    main()