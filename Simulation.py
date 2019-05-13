import orca
import shutil
import warnings
warnings.filterwarnings("ignore")

import os

import models, utils
from urbansim.utils import misc, networks
import output_indicators

data_out = utils.get_run_filename()
print data_out

import sys,statvfs

# f = os.statvfs("/home")
# freespace=f[statvfs.F_BAVAIL] * f[statvfs.F_BSIZE] / (1048576 * 1024.0)
# if freespace < 10:
#     print freespace, 'GB available. Disk space is too small, stop running'
#     sys.exit()


orca.run(["refiner",
          'build_networks',
          "neighborhood_vars"] +
          orca.get_injectable('repm_step_names') + # In place of ['nrh_simulate', 'rsh_simulate']
          ["increase_property_values"])  # Hack to make more feasibility

orca.run([

    "scheduled_demolition_events",
    "random_demolition_events",
    "scheduled_development_events",
    "refiner",       
    "households_transition",
    "fix_lpr",
    "households_relocation",
    "jobs_transition",
    "jobs_relocation",
    "feasibility",
    "residential_developer",
    "non_residential_developer"] +
    orca.get_injectable('repm_step_names') +  # In place of ['nrh_simulate', 'rsh_simulate']
    ["increase_property_values"] +  # Hack to make more feasibility
    orca.get_injectable('hlcm_step_names') +
    orca.get_injectable('elcm_step_names') +
    ["elcm_home_based",
    "jobs_scaling_model",
    "gq_pop_scaling_model",
    # "travel_model", Fixme: on hold
    ],
    iter_vars=range(2016, 2045 + 1),
    data_out='runs/run_official.h5',
    out_base_tables=['jobs', 'base_job_space',
                     'households', 'persons', 'buildings', 'parcels', 'zones', 'semmcds', 'counties','large_areas'],
    out_run_tables=['buildings', 'jobs', 'base_job_space', 'parcels', 'households', 'persons'],
    out_interval=10,
    compress=True)

# output_indicators.main(data_out)

# dir_out = data_out.replace('.h5', '')
# shutil.copytree(dir_out, '/semcog_urbansim/runs/' + os.path.basename(os.path.normpath(dir_out)))
# shutil.copy(data_out, '/mnt/hgfs/J')
