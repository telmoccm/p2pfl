#
# This file is part of the federated_learning_p2p (p2pfl) distribution
# (see https://github.com/pguijas/p2pfl).
# Copyright (c) 2022 Pedro Guijas Bravo.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Example of a P2PFL MNIST node using a MLP model and a MnistFederatedDM.

This node only starts, create a node2 and connect to it in order to start the federated learning process.
"""

import argparse

from p2pfl.learning.dataset.p2pfl_dataset import P2PFLDataset
from p2pfl.learning.pytorch.lightning_learner import LightningLearner
from p2pfl.learning.pytorch.lightning_model import MLP, LightningModel
from p2pfl.nodes.proxy_node import ProxyNode
from p2pfl.utils.utils import set_test_settings

set_test_settings()


def __get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P2PFL MNIST node using a MLP model and a MnistFederatedDM.")
    parser.add_argument("--addr", type=str, help="The port.", required=True)
    return parser.parse_args()


def proxy_node(addr: str) -> None:
    node = ProxyNode(LightningModel(MLP()), address=addr, learner=LightningLearner)
    node.start()

    input("Press any key to start learning\n")

    node.set_start_learning(rounds=2, epochs=1)

    input("Press any key to stop\n")

    node.stop()


if __name__ == "__main__":
    args = __get_args()
    proxy_node(args.addr)