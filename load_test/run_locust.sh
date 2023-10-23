export ENDPOINT_NAME=http://127.0.0.1:8080

export CONTENT_TYPE=application/json
export USERS=20
export WORKERS=5
export RUN_TIME=10m
export LOCUST_UI=true # Use Locust UI
export SCRIPT=locustfile.py
export RESULT_CSV_PREFIX="results_${USERS}_${WORKERS}"

#  == locust options: https://docs.locust.io/en/stable/configuration.html ==
# --master:  Set locust to run in distributed mode with this process as master.
# --expect-workers: How many workers master should expect to connect before starting the test.
# --users: Peak number of concurrent Locust users.
# --run-time: Stop after the specified amount of time.

if $LOCUST_UI ; then
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS --users $USERS --run-time $RUN_TIME --csv $RESULT_CSV_PREFIX &
else
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS --users $USERS --run-time $RUN_TIME --csv $RESULT_CSV_PREFIX --headless &
fi

for (( c=1; c<=$WORKERS; c++ ))
do
    locust -f $SCRIPT -H $ENDPOINT_NAME --worker --master-host=localhost &
done