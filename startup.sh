#Using local scheduler
#Change module and task names
python -m luigi --module extract-config-data-pipeline ExtractFeaturesTemplateDataTask --local-scheduler
python -m luigi --module cdr-data-pipeline JoinCdrAndClusterConfigDataTask --local-scheduler