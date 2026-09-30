#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

from jupyter_client import KernelManager
import queue

import lemma.services.timer as timer


class CodeRunner():

    kernels = dict()

    def run(kernel_id, computation_id, code):
        if kernel_id not in CodeRunner.kernels:
            CodeRunner.start_kernel(kernel_id)

        if computation_id in CodeRunner.kernels[kernel_id]['msg_ids_by_computation_id']:
            msg_id = CodeRunner.kernels[kernel_id]['msg_ids_by_computation_id'][computation_id]
            del(CodeRunner.kernels[kernel_id]['computation_ids_by_msg_id'][msg_id])
            del(CodeRunner.kernels[kernel_id]['msg_ids_by_computation_id'][computation_id])

        msg_id = CodeRunner.kernels[kernel_id]['client'].execute(code)
        CodeRunner.kernels[kernel_id]['computation_ids_by_msg_id'][msg_id] = computation_id
        CodeRunner.kernels[kernel_id]['msg_ids_by_computation_id'][computation_id] = msg_id

    def restart_kernel(kernel_id):
        if kernel_id in CodeRunner.kernels:
            CodeRunner.stop_kernel(kernel_id)
        CodeRunner.start_kernel(kernel_id)

    def start_kernel(kernel_id):
        kernel = {'manager': None, 'client': None}
        kernel['manager'] = KernelManager(kernel_name='python3')
        kernel['manager'].start_kernel()
        kernel['client'] = kernel['manager'].client()
        kernel['client'].start_channels()
        kernel['client'].wait_for_ready()
        kernel['computation_ids_by_msg_id'] = dict()
        kernel['msg_ids_by_computation_id'] = dict()
        CodeRunner.kernels[kernel_id] = kernel

    def stop_all():
        for kernel_id in list(CodeRunner.kernels):
            CodeRunner.stop_kernel(kernel_id)

    def stop_kernel(kernel_id):
        if kernel_id not in CodeRunner.kernels:
            return

        CodeRunner.kernels[kernel_id]['client'].stop_channels()
        CodeRunner.kernels[kernel_id]['manager'].shutdown_kernel(now=True, restart=False)
        del(CodeRunner.kernels[kernel_id])

    def get_running_computations(kernel_id):
        if kernel_id not in CodeRunner.kernels:
            return []

        return list(CodeRunner.kernels[kernel_id]['msg_ids_by_computation_id'])

    @timer.timer
    def fetch_results(kernel_id):
        if kernel_id not in CodeRunner.kernels:
            return []

        result = []
        while True:
            messages = []
            try:
                messages.append(CodeRunner.kernels[kernel_id]['client'].get_iopub_msg(timeout=0.0000001))
            except queue.Empty: pass
            try:
                messages.append(CodeRunner.kernels[kernel_id]['client'].get_shell_msg(timeout=0.0000001))
            except queue.Empty: pass
            if len(messages) == 0:
                break

            for msg in messages:
                if msg['msg_type'] == 'execute_result':
                    orig_msg_id = msg['parent_header']['msg_id']
                    if orig_msg_id in CodeRunner.kernels[kernel_id]['computation_ids_by_msg_id']:
                        computation_id = CodeRunner.kernels[kernel_id]['computation_ids_by_msg_id'][orig_msg_id]
                        result.append({'computation_id': computation_id, 'result': msg['content']})
                elif msg['msg_type'] == 'status' and 'execution_state' in msg['content']:
                    if msg['content']['execution_state'] == 'idle':
                        orig_msg_id = msg['parent_header']['msg_id']
                        if orig_msg_id in CodeRunner.kernels[kernel_id]['computation_ids_by_msg_id']:
                            computation_id = CodeRunner.kernels[kernel_id]['computation_ids_by_msg_id'][orig_msg_id]
                            del(CodeRunner.kernels[kernel_id]['computation_ids_by_msg_id'][orig_msg_id])
                            del(CodeRunner.kernels[kernel_id]['msg_ids_by_computation_id'][computation_id])

        return result


