from typing import Union, List

import logging

from dataclass_utils import dataclass_from_dict
from helpermodules.cli import run_using_positional_cli_args
from modules.common import store
from modules.common.abstract_device import DeviceDescriptor
from modules.common.abstract_soc import AbstractSoc, SocUpdateData
from modules.common.component_context import SingleComponentUpdateContext
from modules.common.component_state import CarState
from modules.common.fault_state import ComponentInfo
from modules.vehicles.bmw import api
from modules.vehicles.bmw.config import BMW, BMWConfiguration


log = logging.getLogger(__name__)


class Soc(AbstractSoc):
    def __init__(self, device_config: Union[dict, BMW], vehicle: int):
        self.config = dataclass_from_dict(BMW, device_config)
        self.vehicle = vehicle
        self.store = store.get_car_value_store(self.vehicle)
        self.component_info = ComponentInfo(self.vehicle, self.config.name, "vehicle")

    def update(self, soc_update_data: SocUpdateData) -> None:
        with SingleComponentUpdateContext(self.component_info):
            soc, range = api.fetch_soc(
                self.config.configuration.user_id,
                self.config.configuration.password,
                self.config.configuration.vin,
                self.vehicle)
            log.info("bmw: vehicle="+str(self.vehicle) + ", return: soc=" + str(soc)+", range=" + str(range))
            self.store.set(CarState(soc, range))


def bmw_update(user_id: str, password: str, vin: str, charge_point: int):
    log.debug("bmw: user_id="+user_id+"vin="+vin+"charge_point="+str(charge_point))
    Soc(BMW(configuration=BMWConfiguration(charge_point, user_id, password, vin)), charge_point).update(SocUpdateData())


def main(argv: List[str]):
    run_using_positional_cli_args(bmw_update, argv)


device_descriptor = DeviceDescriptor(configuration_factory=BMW)
