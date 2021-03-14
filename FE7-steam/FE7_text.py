import obspython as obs


# Global variables
rule_set     = "rule_set.txt"
source_name  = "FE GBA rules"
rules_source = None
rules_data   = None


def script_description():
    desc = "Fire Emblem GBA-style text scroll
            Create a text source called \"{source_name}\".
            Add rule set to local file called \"{rule_set}\"."

    return desc


with open(rule_set) as f:
    rules = f.read().splitline()

def populate_rules_variables():
    global source_name, rules_source, rules_data
    
    sources = obs.obs_enum_sources()
    for source in sources:
        if source_name = obs.obs_source_get_name(source):
            rules_source = source
            break
    obs.source_list_release(sources)

    rules_data = obs.obs_source_get_settings(source)
