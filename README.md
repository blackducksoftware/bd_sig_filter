# bd_sig_filter
BD Script to ignore components matched from Signature scan likely to be partial or invalid matches.

# INTRODUCTION
Black Duck Signature matching is a unique and powerful way to find OSS and 3rd party code within your applications and
environments.

Signature matching uses hierarchical folder analysis to find matches with depth, identifying the strongest match for components.
Most competitive SCA solutions use individual file matching which is not effective to identify component matches
because the majority of files in a component do not change between versions, so multiple matches will be identified for every file.

However, Signature matching can produce false positive matches, especially where template code hierarchies is repeated across
multiple components.

Furthermore, Signatures matches can be identified in folders containing Synopsys tools, or in cache and configuration
locations or test folders which can be ignored at scan time, but may exist in the Black Duck project. Additionally, when scanning
modified OSS, Signature scanning can result in more than 1 match for a component leading to the requirement
to curate the BOM to ignore components.

This script uses several techniques to examine the Signature match paths for components, looking for the component
name and version in the path to determine matches which are likely correct and optionally marking them as reviewed.

It can ignore components only matched from paths which should be excluded (Synopsys tools, cache/config folders 
and test folders), and components which are duplicates across versions where the version string is not found
in the signature match path.

Options can be used to enable ignore and review actions, and other features.

# INSTALLATION

# USAGE

# WORKFLOW


