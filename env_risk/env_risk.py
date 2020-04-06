#python3
# -*- coding: utf-8 -*-


#See data_schema.txt for more details
standard_dict = {
    'last_update':None,
    'country_region-name':None,
    'country_region-ID':None,
    'province_state-name':None,
    'province_state-ID':None,
    'town_area_name':None,
    'town_area_ID':None,
    'total_population':None,
    'latitude':None,
    'longitude':None,
    'confirmed_cases':None,  #   (hospitalised_with_symptoms + intensive_care + quarantine_at_home)
    'new_confirmed_cases':None,
    'hospitalised_all':None,
    'hospitalised_with_symptoms':None,
    'quarantine_at_home':None,
    'intensive_care':None,
    'deaths':None,
    'recovered_out-of-hospital':None,
    'tested':None,
    'average_velocity':None,
    }

def read_italy_official_situation(granularity='regioni'):
    '''
    Read Offical Data from the Italian Governement / Protezione Civile.
    Downloaded from GitHub in JSON format.
    Currently only province_state ("regioni") level is implemented

    Parameters
    ----------
        granularity: str
            spational resolution, either "regioni" or "provincie"

    Returns
    -------
        standardised_data_list: list
            Data at the "regioni" or "provincie" level
    '''
    italy_regioni_population_dict = {
        'Lombardia':10060574,
        'Lazio': 5879082,
        'Campania':5801692, 
        'Sicilia':4999891,
        'Veneto':4905854,
        'Emilia-Romagna':4459477,
        'Piemonte':4356406,
        'Puglia':4029053,
        'Toscana':3729641,
        'Calabria':1947131,
        'Sardegna':1639591,
        'Liguria':1550640,
        'Marche':1525271,
        'Abruzzo':1311580,
        'Friuli Venezia Giulia':1215220,
        #'Trentino-Alto Adige':1072276,
        'P.A. Trento': 538223,
        'P.A. Bolzano': 520891, 
        'Umbria':882015,
        'Basilicata':562869,
        'Molise':305617,
        "Valle d'Aosta":125666,
    }

    import json,sys,wget
    from copy import deepcopy
    
    print('Download')
    if granularity=='regioni':
        filename = wget.download('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json')
    elif granularity=='provincie':
        sys.exit('granularity="provincie" not implemented!')
    else:
        sys.exit('granularity {} not recognised'.format(granularity))
    with open(filename,'r') as f:
        data_list= json.load(f)

    
    standardised_data_list = []
    for county_dict in data_list:
        data_dict = deepcopy(standard_dict)
        data_dict['last_update'] = county_dict['data']
        data_dict['country_region-name'] = county_dict['stato']
        data_dict['province_state-name'] = county_dict['denominazione_regione']
        data_dict['province_state-ID'] = county_dict['codice_regione']
        if granularity=='provincie':
            data_dict['town_area-name'] = county_dict['denominazione_provincia']
            data_dict['town_area-ID'] = county_dict['codice_provincia']
        if granularity=='regioni':
            data_dict['total_population'] = italy_regioni_population_dict[data_dict['province_state-name']]
        elif granularity=='provincie':
            sys.exit('granularity="provincie" not implemented!')
            #data_dict['total_populaiton'] = italy_provincie_population_dict[data_dict['town_area-name']]
        data_dict['latitude'] = county_dict['lat']
        data_dict['longitude'] = county_dict['long']
        data_dict['confirmed_cases'] = county_dict['totale_positivi']
        data_dict['hospitalised_all'] = county_dict['totale_ospedalizzati']
        data_dict['hospitalised_with_symptoms'] = county_dict['ricoverati_con_sintomi']
        data_dict['quarantine_at_home'] = county_dict['isolamento_domiciliare']
        data_dict['intensive_care'] = county_dict['terapia_intensiva']
        data_dict['new_confirmed_cases'] = county_dict['variazione_totale_positivi']
        data_dict['deaths'] = county_dict['deceduti']
        data_dict['recovered_out-of-hospital'] = county_dict['dimessi_guariti']
        data_dict['tested'] = county_dict['tamponi']
        data_dict['average_velocity'] = None
        standardised_data_list.append(data_dict)
    return standardised_data_list


def environmental_risk_factor_basicgasmodel(rho_eff_contagious,sigma=4,v_avg=1.157):
    '''
    Function to compute the environmental risk factor
    based on the collision frequency in the kinetic theory of gases.

        z = sigma * v_avg * rho_eff-contagious

    Parameters
    ----------
        rho_eff_contagious : float
            Estimated (effective) density of contagious individuals
        sigma : float
            "Cross section", 2*infection_radius for a purely 2D model
            Default is 4 meters
        v_avg : float
            Average mobility, expressed as a velocity (m/s)
            Default is 1km/day -> (1.157 1e-5 m/s)
    Returns
    -------
        z : float
            Environmental risk factor
    '''

    return rho_eff_contagious * sigma * v_avg


if __name__ == "__main__":
    print('Example - Italy Data')
    data_list = read_italy_official_situation()
    print('\n')
    l = []
    for data_dict in data_list:
        rho_eff_contagious = data_dict['confirmed_cases']/float(data_dict['total_population'])
        risk = environmental_risk_factor_basicgasmodel(rho_eff_contagious,sigma=4,v_avg=1.157)
        l.append([data_dict['province_state-name'],risk])
        print('{} Environmental Risk Factor= {:f}'.format(data_dict['province_state-name'],risk))
    print('-----\nSorting\n-----')
    [print('{}: ERF={:f}'.format(i[0],i[1])) for i in sorted(l, key = lambda x: x[1])]