# Copyright 2023 BentoML Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import click
import inflection
import orjson

import bentoml
import openllm
from bentoml._internal.utils import human_readable_size

from .. import termui
from .._factory import LiteralOutput
from .._factory import output_option

@click.command("list_bentos", context_settings=termui.CONTEXT_SETTINGS)
@output_option(default_value="json")
@click.pass_context
def cli(ctx: click.Context, output: LiteralOutput) -> None:
  """List available bentos built by OpenLLM."""
  mapping = {
      k: [{"tag": str(b.tag), "size": human_readable_size(openllm.utils.calc_dir_size(b.path)), "models": [{"tag": str(m.tag), "size": human_readable_size(openllm.utils.calc_dir_size(m.path))} for m in (bentoml.models.get(_.tag) for _ in b.info.models)]}
          for b in tuple(i for i in bentoml.list() if all(k in i.info.labels for k in {"start_name", "bundler"})) if b.info.labels["start_name"] == k] for k in tuple(inflection.dasherize(key) for key in openllm.CONFIG_MAPPING.keys())
  }
  mapping = {k: v for k, v in mapping.items() if v}
  if output == "pretty":
    import tabulate
    tabulate.PRESERVE_WHITESPACE = True
    termui.echo(tabulate.tabulate([(k, i["tag"], i["size"], [_["tag"] for _ in i["models"]]) for k, v in mapping.items() for i in v], tablefmt="fancy_grid", headers=["LLM", "Tag", "Size", "Models"]), fg="white")
  else:
    termui.echo(orjson.dumps(mapping, option=orjson.OPT_INDENT_2).decode(), fg="white")
  ctx.exit(0)
