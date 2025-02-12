from typing import Union, List

import logging

from dataclass_utils import dataclass_from_dict
from helpermodules.cli import run_using_positional_cli_args
from modules.common import store
from modules.common.abstract_device import DeviceDescriptor
from modules.common.abstract_soc import AbstractSoc
from modules.common.component_context import SingleComponentUpdateContext
from modules.common.component_state import CarState
from modules.common.fault_state import ComponentInfo
from modules.vehicles.vwid import api
from modules.vehicles.vwid.config import VWId, VWIdConfiguration


log = logging.getLogger(__name__)


class Soc(AbstractSoc):
    def __init__(self, device_config: Union[dict, VWId], vehicle: int):
        self.config = dataclass_from_dict(VWId, device_config)
        self.vehicle = vehicle
        self.store = store.get_car_value_store(self.vehicle)
        self.component_info = ComponentInfo(self.vehicle, self.config.name, "vehicle")

    def update(self, charge_state: bool = False) -> None:
        with SingleComponentUpdateContext(self.component_info):
            soc, range, soc_ts = api.fetch_soc(
                self.config,
                self.vehicle)
            log.info("Result: soc=" + str(soc)+", range=" + str(range) + "@" + soc_ts)
            if soc > 0 and range > 0.0:
                self.store.set(CarState(soc, range))
            else:
                log.error("Result not stored: soc=" + str(soc)+", range=" + str(range))


def vwid_update(user_id: str, password: str, vin: str, refreshToken: str, charge_point: int):
    log.debug("vwid: userid="+user_id+"vin="+vin+"charge_point="+str(charge_point))
    Soc(VWId(configuration=VWIdConfiguration(user_id, password, vin, refreshToken)), charge_point).update(False)


def main(argv: List[str]):
    run_using_positional_cli_args(vwid_update, argv)


device_descriptor = DeviceDescriptor(configuration_factory=VWId)
