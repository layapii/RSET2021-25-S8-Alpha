"use client"
import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList,} from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger,} from "@/components/ui/popover"

const categories = [
  {
    value: "disaster, accident and emergency incident",
    label: "Disaster & accident",
  },
  {
    value: "human interest",
    label: "Human interest",
  },
  {
    value: "politics",
    label: "Politics",
  },
  {
    value: "education",
    label: "Education",
  },
  {
    value: "crime, law and justice",
    label: "Crime, law & justice",
  },
  {
    value: "economy, business and finance",
    label: "Economy, business & finance",
  },
  {
    value: "conflict, war and peace",
    label: "Conflict, war & peace",
  },
  {
    value: "arts, culture, entertainment and media",
    label: "Arts, culture & media",
  },
  {
    value: "labour",
    label: "Labour",
  },
  {
    value: "weather",
    label: "Weather",
  },
  {
    value: "religion",
    label: "Religion",
  },
  {
    value: "society",
    label: "Society",
  },
  {
    value: "health",
    label: "Health",
  },
  {
    value: "environment",
    label: "Environment",
  },
  {
    value: "lifestyle and leisure",
    label: "Lifestyle and leisure",
  },
  {
    value: "science and technology",
    label: "Science and technology",
  },
  {
    value: "sport",
    label: "Sport",
  },
];

export function Combobox({ onSelect}) {
  const [open, setOpen] = React.useState(false)
  const [value, setValue] = React.useState("")

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[275px] justify-between"
        >
          {value
            ? categories.find((category) => category.value === value)?.label
            : "All Categories"}
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search category" />
          <CommandList>
            <CommandEmpty>No category found.</CommandEmpty>
            <CommandGroup>
              {categories.map((category) => (
                <CommandItem
                  key={category.value}
                  value={category.value}
                  onSelect={(currentValue) => {
                    setValue(currentValue === value ? "" : currentValue)
                    setOpen(false)
                    onSelect(currentValue === value ? "" : currentValue)
                  }}
                >
                  {category.label}
                  <Check
                    className={cn(
                      "ml-auto",
                      value === category.value ? "opacity-100" : "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
