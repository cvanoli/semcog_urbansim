import orca
import warnings
warnings.filterwarnings("ignore")

import os
import models, utils, dataset
from urbansim.utils import misc, networks

models_1 = orca.get_injectable('elcm_step_names_regional_accessvars')
models_2 = orca.get_injectable('hlcm_step_names_regional_accessvars')
models_3 = orca.get_injectable('repm_step_names_regional')
orca.run(["refiner",
          'build_networks'] +
          orca.get_injectable('repm_step_names_regional') + # In place of ['nrh_simulate', 'rsh_simulate']
          ["increase_property_values"]+ ["neighborhood_vars",
    "households_transition",
    "households_relocation",
    "jobs_transition",
    "jobs_relocation",
    "feasibility",
    "residential_developer",
    "non_residential_developer"] +
     models_3 +  # In place of ['nrh_simulate', 'rsh_simulate']
     models_2 +
         models_1)


# import orca
# import shutil
# import warnings
# warnings.filterwarnings("ignore")
#
# import os
#
# import models, utils
# from urbansim.utils import misc, networks
#
#
# orca.run(["refiner",
#           'build_networks'] +
#           orca.get_injectable('repm_step_names_regional') + # In place of ['nrh_simulate', 'rsh_simulate']
#           ["increase_property_values"])  # Hack to make more feasibility
#
# orca.run(["neighborhood_vars",
#     "scheduled_demolition_events",
#     "random_demolition_events",
#     "scheduled_development_events",
#     "refiner",
#     "households_transition",
#     "fix_lpr",
#     "households_relocation",
#     "jobs_transition",
#     "jobs_relocation",
#     "feasibility",
#     "residential_developer",
#     "non_residential_developer"] +
#     orca.get_injectable('repm_step_names_regional') +  # In place of ['nrh_simulate', 'rsh_simulate']
#     ["increase_property_values"] +  # Hack to make more feasibility
#     orca.get_injectable('hlcm_step_names_regional_accessvars') +
#     orca.get_injectable('elcm_step_names_regional_accessvars') +
#     ["elcm_home_based",
#     "jobs_scaling_model",
#     "gq_pop_scaling_model",
#     # "travel_model", Fixme: on hold
#     ],
#     iter_vars=range(2016, 2045 + 1),
#     data_out='runs/run_semcog_regional_accessvars.h5',
#     out_base_tables=['jobs', 'base_job_space','households', 'persons', 'buildings', 'parcels',
#                     'zones', 'semmcds', 'counties','large_areas'],
#     out_run_tables=['buildings', 'jobs', 'base_job_space', 'parcels', 'households', 'persons'],
#     out_interval=10,
#     compress=True)
