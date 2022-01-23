from datetime import date
from dataclasses import dataclass
from typing import List

from sqlalchemy import create_engine

from abautomator import config, collector, describer, utils, metrics, analyzer


class InvalidName(Exception):
  pass


@dataclass
class Experiment:
    ctrl_name: str
    tx_names: List[str]
    metrics: List[metrics.ExpMetric]
    start_dt: date
    end_dt: date=None
    name: str=None

    def __post_init__(self):
        self.name = self._get_name(self.ctrl_name, self.tx_names[0])

        assert isinstance(self.metrics[0], metrics.ExpMetric), "Wrong Metric type"
    
    def _get_name(self, ctrl: str, tx: str):
        end = 0
        for i, j in zip(ctrl, tx):
            if i != j:
                return ctrl[:end]
            end += 1

        raise InvalidName("Experiment or Condition Name is invalid")    

    def get_analyzer(self):

        coll = self.get_collector()
        coll.collect_data()

        # init and run the describer
        desc = describer.Describer(
            metrics=coll.metrics
        )
        outcomes_dict = desc.describe_data(self.name)

        return analyzer.Analyzer(
            outcomes=outcomes_dict,
            ctrl_name=self.ctrl_name.replace(self.name, ""),
        )

    def get_collector(self):
        return collector.Collector(
            engine=create_engine(f'bigquery://{config.GCP_PROJECT_ID}'),
            conds=self._get_conds(),
            metrics=self._convert_exp_metrics_to_base_metrics(),
            event="segment_signup_flow_started",
            event_prop="context_traits_onboarding_flow_001",
            start_dt=self.start_dt,
            end_dt=self.end_dt,
        )

    def _get_conds(self) -> List[str]:
        return [self.ctrl_name] + self.tx_names
    
    def _convert_exp_metrics_to_base_metrics(self):
        metric_names = [metric.name for metric in self.metrics]
        metric_name_set = set(metric_names)
        return [
            metrics.METRIC_LOOKUP[name] for name in metric_name_set
        ]

def get_metrics():
    return [
        metrics.METRIC_LOOKUP["granted_location"],
        metrics.METRIC_LOOKUP["granted_notifs"],
    ]
