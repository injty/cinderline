/** A quiet workspace, lit by a single warm lamp. */
type Material = "charcoal" | "copper" | "oak";

interface Room {
  name: string;
  temperature: number;
  materials: Material[];
  lighting: { brightness: number; enabled: boolean };
}

const EVENING_KELVIN = 2700;

export function createRoom(name: string): Room {
  // Leave room for the things that matter.
  return {
    name,
    temperature: EVENING_KELVIN,
    materials: ["charcoal", "copper", "oak"],
    lighting: { brightness: 0.65, enabled: true },
  };
}

export function describeRoom({ name, materials }: Room): string {
  const label = name.replace(/\s+/g, " ").trim();
  return `${label}\nMaterials: ${materials.join(", ")}`;
}

const room = createRoom("Ember Room");
console.log(describeRoom(room));
