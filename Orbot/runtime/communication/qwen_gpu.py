"""Bounded CUDA execution with CPU weight storage for a shared desktop GPU."""


class QwenGpuCapacityError(RuntimeError):
    pass


def gpu_plan(free_bytes, total_bytes, budget_mib=768):
    if budget_mib < 768:
        raise QwenGpuCapacityError("Qwen GPU allocator budget must be at least 768 MiB")
    if free_bytes >= 6 * 1024**3:
        return {"mode":"cuda", "allocator_budget_mib":None}
    if free_bytes < (budget_mib + 256) * 1024**2:
        raise QwenGpuCapacityError(
            f"Qwen3-TTS GPU needs {budget_mib + 256} MiB free for bounded weight offloading; "
            f"currently {free_bytes // 1024**2} MiB is available. CPU inference was not substituted.")
    return {"mode":"cuda_weight_offload", "allocator_budget_mib":budget_mib,
            "allocator_fraction":budget_mib * 1024**2 / total_bytes}


def residency_map(model, anchors=(), resident_subtrees=()):
    """Avoid parent/child residency overlap, including weight parametrizations."""
    result = {}
    for name, module in model.named_modules():
        if any(name == prefix or name.startswith(prefix + '.') for prefix in resident_subtrees):
            continue
        if list(module.parameters(recurse=False)) or list(module.buffers(recurse=False)):
            result[name] = 'cuda:0' if name in anchors else 'cpu'
    for prefix in resident_subtrees:
        model.get_submodule(prefix)  # Fail explicitly on an incompatible model.
        result[prefix] = 'cuda:0'
    return result


def configure_weight_offload(wrapper, torch, plan):
    from accelerate import dispatch_model
    device = torch.device('cuda:0')
    torch.cuda.set_per_process_memory_fraction(plan['allocator_fraction'], 0)
    model = wrapper.model
    anchor = next(model.named_parameters())[0].rsplit('.', 1)[0]
    predictor_anchor = 'talker.code_predictor.' + next(model.talker.code_predictor.named_parameters())[0].rsplit('.', 1)[0]
    dispatch_model(model, device_map=residency_map(model, (anchor, predictor_anchor)),
                   main_device=device, offload_buffers=True, force_hooks=True,
                   preload_module_classes=['Qwen3TTSTalkerDecoderLayer', 'Qwen3TTSDecoderLayer'])
    wrapper.device = device
    codec = model.speech_tokenizer
    # Codec decode() reads codebook buffers directly, outside Module.forward.
    # Keep that small subtree resident instead of leaving those buffers on meta.
    dispatch_model(codec.model, device_map=residency_map(codec.model, resident_subtrees=('decoder.quantizer',)),
                   main_device=device, offload_buffers=True, force_hooks=True)
    codec.device = device
