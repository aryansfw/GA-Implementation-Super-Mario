using UnityEngine;

// Death Boundary
[RequireComponent(typeof(BoxCollider2D))]
public class DeathBarrier : MonoBehaviour
{
  private void OnTriggerEnter2D(Collider2D other)
  {
    if (other.CompareTag("Player"))
    {
      other.gameObject.SetActive(false);
    }
  }

}
