#Using local scheduler
#To use central scheduler and see progress of ongoing tasks on a web interface, use central scheduler

# The two scripts need to be run in this order - the extract-config-data-pipeline going first

python -m luigi --module extract-config-data-pipeline ExtractFeaturesTemplateDataTask --local-scheduler
python -m luigi --module cdr-data-pipeline GetVisualisationsTask --local-scheduler
