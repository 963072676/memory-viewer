"""Memory Clustering API router (F-40)."""

from fastapi import APIRouter, HTTPException, Query

from app.services.clustering_service import compute_clusters, get_cluster_detail, invalidate_cache

router = APIRouter()


@router.get("")
def list_clusters(force: bool = Query(default=False)):
    """Get all memory clusters.
    
    AC-F40-1: Returns >=3 meaningful clusters.
    AC-F40-2: Each cluster has an understandable name.
    AC-F40-5: Cluster generation completes in <10s for 100 memories.
    """
    clusters = compute_clusters(force_refresh=force)
    return {
        "clusters": clusters,
        "total": len(clusters),
        "total_memories": sum(c["count"] for c in clusters),
    }


@router.get("/{cluster_id}")
def get_cluster(cluster_id: str):
    """Get detailed information about a specific cluster.
    
    AC-F40-4: Clicking a cluster shows its contained memories.
    """
    cluster = get_cluster_detail(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
    return cluster


@router.post("/refresh")
def refresh_clusters():
    """Force refresh cluster cache.
    
    AC-F40-6: Clusters auto-update after new memories are added.
    """
    invalidate_cache()
    clusters = compute_clusters(force_refresh=True)
    return {
        "success": True,
        "message": "Clusters refreshed",
        "total_clusters": len(clusters),
    }
