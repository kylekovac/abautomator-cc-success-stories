import copy
import dill as pickle
import os

import pytest
from abautomator import collector, metrics


from tests import utils

from abautomator import describer, analyzer
from abautomator.exp_config import EXP_NAME, CTRL_NAME, CONDS, EVENT,EVENT_PROP, DT_RANGE

@pytest.mark.build
def test_get_objects(local_coll):
    
    print("Collecting data (this could take 10+ mins)")
    local_coll.collect_data()

    local_coll.engine = None
    utils.cache_obj(local_coll, f"{EXP_NAME}_coll")
    print("Data Collected! Generating Analyzers")

    _generate_analyzers()

@pytest.mark.build
def test_get_collector(local_coll):
    
    local_coll.collect_data()
    assert len(local_coll.metrics) > 0
    assert len(local_coll.metrics[0].user_metric_df) > 0

    local_coll.engine = None
    utils.cache_obj(local_coll, f"{EXP_NAME}_coll")

@pytest.mark.build
def test_generate_analyzers():
    _generate_analyzers()


def _generate_analyzers():
    local_coll = pickle.load(
        open(
            utils.get_cache_path(f"{EXP_NAME}_coll"), "rb")
    )
    for mapping in [
            (None, "all"),
            ("device_type","android"),
            ("device_type", "ios"),
            ("user_type","new"),
            ("user_type", "existing"),
        ]:
        curr_coll = copy.deepcopy(local_coll)
        column, value = mapping
        if value != "all":
            column, value = mapping
            curr_coll = _filter_coll_metrics(curr_coll, column=column, value=value)

        print(f"Describing data for {value}")
        desc = describer.Describer(
            metrics=curr_coll.metrics
        )
        outcomes_dict = desc.describe_data(exp_name=EXP_NAME)
        
        print(f"Analyzing data for {value}")
        analy =  analyzer.Analyzer(
            outcomes=outcomes_dict,
            ctrl_name=CTRL_NAME,    
        )

        pickle.dump(
            analy, open(utils.get_cache_path(f"{EXP_NAME}_analy_{value}"), "wb")
        )

def _filter_coll_metrics(coll, column, value):
    for metric in coll.metrics:
        metric.user_metric_df = metric.user_metric_df[metric.user_metric_df[column] == value]
    
    return coll

@pytest.fixture
def local_coll(engine):
    return collector.Collector(
        engine=engine,
        conds=CONDS,
        metrics=[
            # Primary metrics
            metrics.METRIC_LOOKUP["feed_views"],
            metrics.METRIC_LOOKUP["feed_taps"],
            metrics.METRIC_LOOKUP["all_feed_shares"],
            metrics.METRIC_LOOKUP["direct_feed_shares"],
            metrics.METRIC_LOOKUP["indirect_feed_shares"],
            metrics.METRIC_LOOKUP["signup_activation"],
            metrics.METRIC_LOOKUP["trial_starts"],
            metrics.METRIC_LOOKUP["protect_payment_successful"],
            metrics.METRIC_LOOKUP["protect_cancellations"],

            # Secondary metrics
            metrics.METRIC_LOOKUP["all_sessions"],
            metrics.METRIC_LOOKUP["organic_sessions"],
            metrics.METRIC_LOOKUP["push_driven_sessions"],
            metrics.METRIC_LOOKUP["incident_views"],
            metrics.METRIC_LOOKUP["incident_share_attempts"],          

            # Guardrail matrics
            metrics.METRIC_LOOKUP["chats"],
            metrics.METRIC_LOOKUP["friend_invites"],
            metrics.METRIC_LOOKUP["trial_starts"],
        ],
        event=EVENT,
        event_prop=EVENT_PROP,
        dt_range=DT_RANGE,
    )
