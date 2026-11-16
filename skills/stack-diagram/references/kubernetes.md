# Kubernetes diagrams

Read this when the stack runs on Kubernetes. The icons are the official kubernetes/community icon set, and the diagram keeps the normal style.

## Icons

```bash
python3 scripts/fetch_icons.py <job>/icons --allow-network "k8s:kubernetes" "ing:k8s/ingress" "svc:k8s/service" "deploy:k8s/deployment" "pod:k8s/pod"
```

- `name:k8s/<Resource>` needs `--allow-network`. Offline, the node gets a pictogram.
- The fetch reads one pinned commit of kubernetes/community (icons under Apache-2.0 or CC-BY-4.0; the logo is a Linux Foundation trademark) from `raw.githubusercontent.com`, path `icons/svg/` only. A branch is never used, so the icons cannot change under a diagram. The pin moves only through an upstream review.
- Resources and infrastructure use the unlabeled variants, which stay clean at diagram scale. Control plane components use the labeled variants, which are the only ones the set has for them.
- Short names and plurals work: `svc`, `ing`, `deploy`, `po`, `cm`, `sts`, `ds`, `ns`, `pv`, `pvc`, `sa`, `hpa`, `netpol`, `crd`, `node`, and `api`, `scheduler`, `kubelet`, `kube-proxy`, `controller-manager`. A miss prints every name.
- Always write the `k8s/` prefix for a resource. `k8s:kubernetes` (the bare slug) is the Kubernetes wheel through the usual chain, for the cluster's group label. A slug such as `kubernetes-dashboard` is a different product and stays on the usual chain.
- **Credit:** `build.py` credits source `k8s` as `Kubernetes icons`.

## Drawing rules

- **Keep the normal tile style.** Icons go on the normal white `tile`, so they sit beside NGINX, cert-manager, databases and cloud load balancers without a second visual language. `tile bare` is for a lone glyph only.
- **Groups use the template's own groups.** Draw a cluster, namespace or node with `ga`, `ga-nested` or `gb`, labelled in Kubernetes' casing (`Namespace: prod`). No Kubernetes group style is added.
- **Names:** the resource kind beside its icon (`Ingress`, `Deployment`) and the workload's own name in the role line.
- **Edges and legend** stay as in the template.
- A vendor's rules cover only its own group. A user, a CDN or an external database beside the cluster keeps the normal tiles, groups and edges.
