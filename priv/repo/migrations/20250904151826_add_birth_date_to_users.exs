defmodule BorutaExample.Repo.Migrations.AddBirthDateToUsers do
  use Ecto.Migration

  def change do
    alter table(:users) do
      add :birth_date, :date
    end
  end
end
