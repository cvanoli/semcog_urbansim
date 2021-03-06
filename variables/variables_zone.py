import numpy as np
import orca
import pandas as pd


#####################
# ZONES VARIABLES
#####################

@orca.column('zones', cache=True, cache_scope='iteration')
def popden(parcels, households):
    return households.persons.groupby(households.zone_id).sum() / parcels.acres.groupby(parcels.zone_id).sum()

@orca.column('zones', cache=True, cache_scope='iteration')
def ln_popden(zones):
    return np.log1p(zones.popden).fillna(0)

@orca.column('zones', cache=True, cache_scope='iteration')
def households(households):
    return households.zone_id.groupby(households.zone_id).size()

@orca.column('zones', cache=True, cache_scope='iteration')
def population(households):
    return households.persons.groupby(households.zone_id).sum()
@orca.column('zones', cache=True, cache_scope='iteration')
def ln_population(zones):
    return np.log1p(zones.population).fillna(0)

@orca.column('zones', cache=True, cache_scope='iteration')
def buildings(buildings):
    return buildings.zone_id.groupby(buildings.zone_id).size()
@orca.column('zones', cache=True, cache_scope='iteration')
def bldg_sqft_den(parcels, buildings):
    return buildings.building_sqft.groupby(buildings.zone_id).sum() / parcels.acres.groupby(parcels.zone_id).sum()
@orca.column('zones', cache=True, cache_scope='iteration')
def ln_bldg_sqft_den(zones):
    return np.log1p(zones.bldg_sqft_den).fillna(0)

@orca.column('zones', cache=True)
def jobs_within_30_min(jobs, travel_data):
    from urbansim.utils import misc
    j = pd.DataFrame({'zone_id': jobs.zone_id})
    td = travel_data.to_frame()
    zone_ids = np.unique(td.reset_index().to_zone_id)
    return misc.compute_range(td,
                              j.groupby('zone_id').size().reindex(index=zone_ids).fillna(0),
                              "am_auto_total_time",
                              30, agg=np.sum)

@orca.column('zones', cache=True, cache_scope='iteration')
def empden(zones, parcels,):
    return zones.employment / parcels.acres.groupby(parcels.zone_id).sum()
@orca.column('zones', cache=True, cache_scope='iteration')
def ln_empden(zones):
    return np.log1p(zones.empden).fillna(0)


@orca.column('zones', cache=True, cache_scope='iteration')
def percent_vacant_job_spaces(buildings):
    buildings = buildings.to_frame(buildings.local_columns + ['job_spaces', 'vacant_job_spaces', 'zone_id'])
    job_spaces = buildings.groupby('zone_id').job_spaces.sum()
    vacant_job_spaces = buildings.groupby('zone_id').vacant_job_spaces.sum()

    return (vacant_job_spaces * 1.0 / job_spaces).replace([np.inf, -np.inf], np.nan).fillna(0)

@orca.column('zones', cache=True, cache_scope='iteration')
def percent_vacant_residential_units(buildings):
    buildings = buildings.to_frame(buildings.local_columns + ['vacant_residential_units', 'zone_id'])
    du = buildings.groupby('zone_id').residential_units.sum()
    vacant_du = buildings.groupby('zone_id').vacant_residential_units.sum()

    return (vacant_du * 1.0 / du).replace([np.inf, -np.inf], np.nan).fillna(0)

def make_employment_density_variable(sector_id):
    """
    Generate zonal employment density variable. Registers with orca.
    """
    var_name = 'ln_empden_%s' % sector_id

    @orca.column('zones', var_name, cache=True, cache_scope='iteration')
    def func():
        zones = orca.get_table('zones')
        jobs = orca.get_table('jobs')
        total_acres = zones.acres
        jobs = jobs.to_frame(jobs.local_columns + ['zone_id'])
        jobs_sector = jobs[jobs.sector_id == sector_id].zone_id.value_counts()
        return np.log1p(jobs_sector / total_acres).fillna(0)

    return func


emp_sectors = np.arange(18) + 1
for sector in emp_sectors:
    make_employment_density_variable(sector)

@orca.column('zones', cache=True, cache_scope='iteration')
def z_total_jobs(jobs):
    return jobs.zone_id.value_counts()

@orca.column('zones', cache=True, cache_scope='iteration')
def mean_age_of_head(households):
    return households.age_of_head.groupby(households.zone_id).mean()

@orca.column('zones', cache=True, cache_scope='iteration')
def mean_hh_size(households):
    return households.persons.groupby(households.zone_id).mean()

@orca.column('zones', cache=True, cache_scope='iteration')
def mean_children(households):
    return households.children.groupby(households.zone_id).mean()

@orca.column('zones', cache=True, cache_scope='iteration')
def mean_income(households):
    return households.income.groupby(households.zone_id).mean()

def prop_household_var(qry, variable, col_name):
    col_name_ = "prop_" + col_name
    @orca.column('zones', col_name_, cache=True, cache_scope='iteration')
    def func(zones, households):
        households = households.to_frame([variable, 'zone_id'])
        return households.query(qry).groupby('zone_id').size() / zones.households
    return func

prop_household_var('race_id == 1', 'race_id', 'race_1')
prop_household_var('race_id == 2', 'race_id', 'race_2')
prop_household_var('race_id == 3', 'race_id', 'race_3')
prop_household_var('race_id == 4', 'race_id', 'race_4')

prop_household_var('children >= 1', 'children', 'hh_with_children')
prop_household_var('persons == 1', 'persons', 'hh_size_1')
prop_household_var('persons == 2', 'persons', 'hh_size_2')
prop_household_var('persons > 2', 'persons', 'hh_size_gt2')
prop_household_var('persons <= 2', 'persons', 'hh_size_lt2')
prop_household_var('persons > 4', 'persons', 'hh_size_gt4')

prop_household_var('income_quartile == 1', 'income_quartile', 'income_1')
prop_household_var('income_quartile == 2', 'income_quartile', 'income_2')
prop_household_var('income_quartile == 3', 'income_quartile', 'income_3')
prop_household_var('income_quartile == 4', 'income_quartile', 'income_4')

@orca.column('zones', cache=True, cache_scope='iteration')
def mean_sqft_per_unit(buildings):
    return buildings.sqft_per_unit.groupby(buildings.zone_id).mean()

@orca.column('zones', cache=True, cache_scope='iteration')
def sum_residential_units(buildings):
    return buildings.residential_units.groupby(buildings.zone_id).sum()

@orca.column('zones', cache=True, cache_scope='iteration')
def sum_non_residential_units(buildings):
    return buildings.non_residential_units.groupby(buildings.zone_id).sum()

@orca.column('zones', cache=True, cache_scope='iteration')
def mean_non_residential_sqft(buildings):
    return buildings.non_residential_sqft.groupby(buildings.zone_id).mean()

def prop_building_var(qry, variable, col_name):
    col_name_ = "prop_" + col_name
    @orca.column('zones', col_name_, cache=True, cache_scope='iteration')
    def func(zones, buildings):
        buildings = buildings.to_frame([variable, 'zone_id'])
        return buildings.query(qry).groupby('zone_id').size() / zones.buildings
    return func

prop_building_var('is_office == 1', 'is_office', 'office_buildings')
prop_building_var('is_industrial == 1', 'is_industrial', 'industrial_buildings')
prop_building_var('is_retail == 1', 'is_retail', 'retail_buildings')
prop_building_var('is_medical == 1', 'is_medical', 'medical_buildings')
prop_building_var('general_type == "Residential"', 'general_type', 'residential_buildings')

@orca.column('zones', cache=True, cache_scope='iteration')
def mean_parcels_size(parcels):
    return parcels.acres.groupby(parcels.zone_id).mean()


@orca.column('zones', cache=True, cache_scope='iteration')
def employment(jobs, travel_data):
    td = travel_data.to_frame()
    zone_ids = np.unique(td.reset_index().to_zone_id)
    j = pd.DataFrame({'zone_id': jobs.zone_id})
    return j.groupby('zone_id').size().reindex(index=zone_ids).fillna(0)


@orca.column('zones', cache=True, cache_scope='iteration')
def retail_jobs(jobs, travel_data):
    td = travel_data.to_frame()
    zone_ids = np.unique(td.reset_index().to_zone_id)
    j = pd.DataFrame({'zone_id': jobs.zone_id, 'sector_id': jobs.sector_id})
    return j.loc[j.sector_id == 5, :].groupby('zone_id').size().reindex(index=zone_ids).fillna(0)


def logsum_based_accessibility(travel_data, zones, name_attribute, spatial_var):
    td = travel_data.to_frame()
    zones = zones.to_frame(['population', 'employment'])

    td = td.reset_index()
    zones = zones.reset_index()
    unique_zone_ids = np.unique(zones.zone_id.values)

    zones.index = zones.index.values + 1
    zone_id_xref = dict(zip(zones.zone_id, zones.index.values))
    apply_xref = lambda x: zone_id_xref[x]

    td = td[td.from_zone_id.isin(unique_zone_ids)]
    td = td[td.to_zone_id.isin(unique_zone_ids)]

    td['from_zone_id2'] = td.from_zone_id.apply(apply_xref)
    td['to_zone_id2'] = td.to_zone_id.apply(apply_xref)

    rows = td['from_zone_id2']
    cols = td['to_zone_id2']

    logsums = 0 * np.ones((rows.max() + 1, cols.max() + 1), dtype=td[name_attribute].dtype)
    logsums.put(indices=rows * logsums.shape[1] + cols, values=td[name_attribute])

    population = zones[spatial_var].values
    population = population[np.newaxis, :]

    zone_ids = zones.index.values
    zone_matrix = population * np.exp(logsums[zone_ids, :][:, zone_ids])
    zone_matrix[np.isnan(zone_matrix)] = 0
    results = pd.Series(zone_matrix.sum(axis=1), index=zones.index.values)
    zones['logsum_var'] = results
    zones = zones.reset_index().set_index('zone_id')
    return zones.logsum_var


@orca.column('zones', cache=True, cache_scope='iteration')
def logsum_pop_high_income(zones, travel_data):
    name_attribute = 'am_work_highinc_logsum'
    spatial_var = 'population'
    return logsum_based_accessibility(travel_data, zones, name_attribute, spatial_var)


@orca.column('zones', cache=True, cache_scope='iteration')
def logsum_pop_low_income(zones, travel_data):
    name_attribute = 'am_work_lowinc_logsum'
    spatial_var = 'population'
    return logsum_based_accessibility(travel_data, zones, name_attribute, spatial_var)


@orca.column('zones', cache=True, cache_scope='iteration')
def logsum_job_high_income(zones, travel_data):
    name_attribute = 'am_work_highinc_logsum'
    spatial_var = 'employment'
    return logsum_based_accessibility(travel_data, zones, name_attribute, spatial_var)


@orca.column('zones', cache=True, cache_scope='iteration')
def logsum_job_low_income(zones, travel_data):
    name_attribute = 'am_work_lowinc_logsum'
    spatial_var = 'employment'
    return logsum_based_accessibility(travel_data, zones, name_attribute, spatial_var)

@orca.column('zones', cache=True, cache_scope='iteration')
def transit_jobs_50min(zones, travel_data):
    td = travel_data.to_frame(['am_transit_total_time']).reset_index()
    zemp = zones.to_frame(['employment'])
    temp = pd.merge(td,zemp, left_on = 'to_zone_id', right_index = True, how='left' )
    transit_jobs_50min = temp[temp.am_transit_total_time <=50].groupby('from_zone_id').employment.sum()
    return transit_jobs_50min


@orca.column('zones', cache=True, cache_scope='iteration')
def transit_jobs_30min(zones, travel_data):
    td = travel_data.to_frame(['am_transit_total_time']).reset_index()
    zemp = zones.to_frame(['employment'])
    temp = pd.merge(td,zemp, left_on = 'to_zone_id', right_index = True, how='left' )
    transit_jobs_30min = temp[temp.am_transit_total_time <=30].groupby('from_zone_id').employment.sum()
    return transit_jobs_30min


@orca.column('zones', cache=True, cache_scope='iteration')
def a_ln_emp_26min_drive_alone(zones, travel_data):
    drvtime = travel_data.to_frame(['am_auto_total_time']).reset_index()
    zemp = zones.to_frame(['employment'])
    temp = pd.merge(drvtime, zemp, left_on ='to_zone_id', right_index = True, how='left' )
    return np.log1p(temp[temp.am_auto_total_time <=26].groupby('from_zone_id').employment.sum().fillna(0))


@orca.column('zones', cache=True, cache_scope='iteration')
def a_ln_emp_50min_transit(zones, travel_data):
    transittime = travel_data.to_frame(['am_transit_total_time']).reset_index()
    zemp = zones.to_frame(['employment'])
    temp = pd.merge(transittime,zemp, left_on = 'to_zone_id', right_index = True, how='left' )
    return np.log1p(temp[temp.am_transit_total_time <=50].groupby('from_zone_id').employment.sum().fillna(0))


@orca.column('zones', cache=True, cache_scope='iteration')
def a_ln_retail_emp_15min_drive_alone(zones, travel_data):
    drvtime = travel_data.to_frame(['midday_auto_total_time']).reset_index()
    zemp = zones.to_frame(['employment'])
    temp = pd.merge(drvtime,zemp, left_on = 'to_zone_id', right_index = True, how='left' )
    return np.log1p(temp[temp.midday_auto_total_time <=15].groupby('from_zone_id').employment.sum().fillna(0))


## NEIGH (NON PANDANA) VARS , ave_nonres_sqft_price

@orca.column('zones', cache=True, cache_scope='iteration')
def percent_hh_with_children(households):
    households = households.to_frame(['has_children', 'zone_id'])
    hh = households.groupby('zone_id').has_children.size()
    children_hh = households.groupby('zone_id').has_children.sum()
    return (children_hh * 1.0 / hh).replace([np.inf, -np.inf], np.nan).fillna(0)

@orca.column('zones', cache=True, cache_scope='iteration')
def percent_low_income(households):
    households = households.to_frame(['low_income', 'zone_id'])
    hh = households.groupby('zone_id').low_income.size()
    low_inc_hh = households.groupby('zone_id').low_income.sum()
    return (low_inc_hh * 1.0 / hh).replace([np.inf, -np.inf], np.nan).fillna(0)


@orca.column('zones', cache=True, cache_scope='iteration')
def ave_res_sqft_price(zones, buildings):
    buildings = buildings.to_frame(['sqft_price_res', 'zone_id'])
    return buildings.groupby('zone_id').sqft_price_res.mean()

@orca.column('zones', cache=True, cache_scope='iteration')
def ave_nonres_sqft_price(zones, buildings):
    buildings = buildings.to_frame(['sqft_price_nonres', 'zone_id'])
    return buildings.groupby('zone_id').sqft_price_nonres.mean()